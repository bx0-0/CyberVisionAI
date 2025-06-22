from django.urls import path
from . import views

app_name = 'Network'

urlpatterns = [
    path('', views.network_view, name='network'),
]
