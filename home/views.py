from django.shortcuts import render

# Create your views here.

def Show_home(request):
    return render(request=request, template_name='home/home.html',context={} )

def Show_about(request):
    return render(request=request, template_name='home/about.html',context={} )

def show_documention(request):
    return render(request=request, template_name='home/documention.html',context={} )