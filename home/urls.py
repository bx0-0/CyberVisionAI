from .views import Show_home, Show_about, show_documention
from django.urls import  path

app_name = 'home'
urlpatterns = [
    path('',Show_home,name='show_home'),
    path('about-us/',Show_about,name='show_about'),
    path('documention/',show_documention,name='show_documention'),
]
