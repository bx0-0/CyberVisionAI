from django.urls import path
from .views import generate_report,show_report,edit_report,list_reports,delete_report

app_name='genReport'

urlpatterns = [
    path('gen-report-form/',generate_report,name='generate_report_form'),
    path('list-reports/',list_reports,name='list_reports'),
    path('<slug>/',show_report,name='show_report'),
    path('<slug>/delete/',delete_report,name='delete_report'),
    path('<slug>/edit/',edit_report,name='edit_report'),
    
]
