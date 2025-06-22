from django.urls import path
from .views import add_vulnerabilities,show_charts,delete_group,list_charts,handle_excel_upload,download_pdf

app_name = 'Security_Indicators'

urlpatterns = [
    path('form/', add_vulnerabilities, name='add_vulnerabilities'),
    path('list/', list_charts, name='list_charts'),
    path('upload/', handle_excel_upload, name='handle_excel_upload'),
    path('charts/<slug>/', show_charts, name='show_charts'),
    path('delete/<slug>/', delete_group, name='delete_group'),
    path('download/<slug>/', download_pdf, name='download_pdf'),
]