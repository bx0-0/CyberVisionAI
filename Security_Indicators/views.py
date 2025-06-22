import shutil
from django.conf import settings
from django.shortcuts import get_object_or_404, render, redirect
from django.forms import ValidationError, formset_factory
from .forms import VulnerabilityForm, UploadFileForm
from .models import Vulnerability, VulnerabilityGroup
from .toolkite import generate_charts,create_pdf_with_images
import os
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
import pandas as pd
from django.core.files.storage import default_storage
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required

@login_required
def add_vulnerabilities(request):
    VulnerabilityFormSet = formset_factory(VulnerabilityForm, extra=1, min_num=1,max_num=6)
    if request.method == "POST":
        formset = VulnerabilityFormSet(request.POST)
        if formset.is_valid():
            group = VulnerabilityGroup(user=request.user)
            group.save()

            vulnerabilities = []
            for form in formset:
                if form.is_valid():
                    vulnerability = form.cleaned_data
                    if vulnerability:
                        vulnerabilities.append(
                            {
                                "vulnerability_type": vulnerability.get("vulnerability_type"),
                                "severity": vulnerability.get("severity"),
                                "count": vulnerability.get("count"), 
                            }
                        )
                    
                    myform = form.save(commit=False)
                    myform.group = group
                    myform.user = request.user
                    myform.save()
                else:
                    raise ValidationError(f"Form errors for form {form}: {form.errors}")  # raise ValidationError errors for debugging

            if vulnerabilities:
                data = {
                    'vulnerability_type': [v['vulnerability_type'] for v in vulnerabilities],
                    'count': [v['count'] for v in vulnerabilities],
                    'severity': [v['severity'] for v in vulnerabilities]
                }

                path = generate_charts(data)
                group.chart_folder = path
                group.save()

            return redirect("Security-Indicators:show_charts", slug=group.slug)
        else:
            raise ValidationError(f"Formset errors: {formset.errors}")  
    else:
        formset = VulnerabilityFormSet()
    
    return render(request, "form.html", {"formset": formset})


@login_required
def show_charts(request, slug):
    group = VulnerabilityGroup.objects.get(slug=slug, user=request.user)
    chart_folder = group.chart_folder
    # Construct the absolute path of the chart folder
    chart_folder = os.path.join(settings.MEDIA_ROOT, chart_folder)
    
    # Extracting all chart links from the folder
    chart_links = [os.path.join(settings.MEDIA_URL, os.path.relpath(os.path.join(chart_folder, f), settings.MEDIA_ROOT)) for f in os.listdir(chart_folder) if os.path.isfile(os.path.join(chart_folder, f))]
    
    return render(request, "chart.html", {"chart_links": chart_links, "slug": slug})

@login_required
def delete_group(request, slug):
    group = get_object_or_404(VulnerabilityGroup, slug=slug, user=request.user)

    chart_folder_path = os.path.join(settings.MEDIA_ROOT, group.chart_folder)

    if os.path.exists(chart_folder_path) and os.path.isdir(chart_folder_path):
        shutil.rmtree(chart_folder_path)

    group.delete()

    return redirect("Security-Indicators:list_charts")

@login_required
def list_charts(request):
    charts = VulnerabilityGroup.objects.filter(user=request.user).order_by('-created_at')

    paginator = Paginator(charts, 4)

    page_number = request.GET.get('page')

    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    return render(request, "charts_list.html", {"groups": page_obj})

@login_required
def handle_excel_upload(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            file = form.cleaned_data['file']
            
            # Save the file temporarily
            file_path = default_storage.save('temp/' + file.name, file)
            path = 'media/'+file_path
            try:
                # Read Excel file
                data = pd.read_excel(path)
                
                # Validate and process the data
                vulnerabilities = []
                for _, row in data.iterrows():
                    # Handle cases where columns might be missing or misnamed
                    vulnerability_type = row.get('Vulnerability Type')
                    count = row.get('Count')
                    severity = row.get('Severity')
                    
                    if pd.notna(vulnerability_type) and pd.notna(count) and pd.notna(severity):
                        vulnerabilities.append(
                            {
                                "vulnerability_type": vulnerability_type,
                                "count": count,
                                "severity": severity,
                            }
                        )
                    else:
                        # Handle missing or invalid data
                        raise ValidationError(f"Missing or invalid data in row: {row}")
                
                if vulnerabilities:
                    data_dict = {
                        'vulnerability_type': [v['vulnerability_type'] for v in vulnerabilities],
                        'count': [v['count'] for v in vulnerabilities],
                        'severity': [v['severity'] for v in vulnerabilities]
                    }

                    # Generate charts
                    path = generate_charts(data_dict)
                    
                    # Create a new vulnerability group
                    group = VulnerabilityGroup(user=request.user)
                    group.save()

                    # Save vulnerabilities to the database
                    for v in vulnerabilities:
                        vulnerability = Vulnerability(
                            vulnerability_type=v['vulnerability_type'],
                            count=v['count'],
                            severity=v['severity'],
                            group=group,
                            user=request.user
                        )
                        vulnerability.save()

                    group.chart_folder = path
                    group.save()

                    # Redirect to show charts page
                    return redirect("Security-Indicators:show_charts", slug=group.slug)
                else:
                    # Handle case with no valid data
                    raise ValidationError("No valid vulnerabilities found in the file.")
            except Exception as e:
                # Handle file reading or processing errors
                raise ValidationError(f"Error processing file: {e}")
            finally:
                # Clean up the file after processing
                default_storage.delete(file_path)
                
    else:
        form = UploadFileForm()
    
    context = {
        'form': form
    }
    return render(request, "excel_upload.html", context)

@login_required
def download_pdf(request, slug):
    # Example image paths
    group  = VulnerabilityGroup.objects.get(slug=slug, user=request.user)
    dir_link = group.chart_folder
    image_paths = os.path.join(settings.MEDIA_ROOT, dir_link)

    if not os.path.exists(image_paths):
        raise FileNotFoundError(f"Directory not found: {image_paths}")

    if not os.path.isdir(image_paths):
        raise NotADirectoryError(f"Not a directory: {image_paths}")

    if not os.listdir(image_paths):
        raise FileNotFoundError(f"Directory is empty: {image_paths}")

    image_paths = [os.path.join(image_paths, f) for f in os.listdir(image_paths) if os.path.isfile(os.path.join(image_paths, f))]

    if not image_paths:
        raise FileNotFoundError(f"Directory is empty: {image_paths}")

    # Create PDF
    pdf_path = create_pdf_with_images(image_paths)

    # Create HTTP response with PDF file
    with open(pdf_path, 'rb') as pdf_file:
        response = HttpResponse(pdf_file.read(), content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="charts.pdf"'

    # Delete the temporary PDF file
    os.remove(pdf_path)

    return response