from django.shortcuts import get_object_or_404, redirect, render
from .forms import GenReportForm,EditReport
from .models import Report
from django.contrib import messages
import markdown 
import html 
from  django.core.paginator import Paginator 
from django.contrib.auth.decorators import login_required
from .tasks import generate_report_task
from django.http import JsonResponse


@login_required
def generate_report(request):
    if request.method == 'POST':
        form = GenReportForm(request.POST, request.FILES)
        if form.is_valid():
            bug_name = form.cleaned_data['bug_name']
            asset = form.cleaned_data['asset']
            step_to_reproduce = form.cleaned_data['step_to_reproduce']
            POC = form.cleaned_data['POC']
            severity = form.cleaned_data['severity']
            model = form.cleaned_data["choice_model"]

            user_id = request.user.id
            task = generate_report_task.delay(user_id,bug_name, asset, step_to_reproduce, POC, severity, model)

           
            return JsonResponse({'task_id': task.id, 'task_status': task.status}, safe=False)
            

    else:
        form = GenReportForm()
    return render(request, 'genReport/report_gen_form.html', {'form': form})


def show_report(request, slug):
    report = get_object_or_404(Report, user=request.user,slug=slug)
    report_content_escape = html.escape(report.report_file)
    report_content = markdown.markdown(report_content_escape, extensions=['tables'])
    report_slug = report.slug

    return render(request, 'genReport/show_report.html', context={'report':report_content, 'report_slug':report_slug,'report_no_html':report_content_escape})

@login_required
def edit_report(request, slug):
    report =  get_object_or_404(Report, user=request.user, slug=slug)
    context = {}
    if request.method == "POST":
        myform= EditReport(request.POST,instance=report)
        if myform.is_valid():
            myform.save()
        return redirect('report-gen:show_report',slug=slug)    
    else:
        myform = EditReport(instance=report)
        context  = {
            'form':myform
        }
    return render(request, "genReport/edit_report.html",context)    

@login_required
def list_reports(request):
    context ={}
    reports = Report.objects.filter(user=request.user).order_by('-create_at')
    paginator = Paginator(reports,4)
    PageNumber = request.GET.get("page")
    page_obj = paginator.get_page(PageNumber)   
    if reports:
        context ={
            'reports':page_obj
        }
    else:
        messages.info(request,message='no  report yet..')
    return render(request,'genReport/listReport.html',context)    

@login_required
def delete_report(request,slug):
    report = get_object_or_404(Report, user=request.user, slug=slug)
    report.delete()
    return redirect('report-gen:list_reports')