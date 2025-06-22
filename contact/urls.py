from django.urls import path 
from . import views


app_name="contact"
urlpatterns = [

       path('', views.send_massage, name='send_massage'),
       path('q&a/', views.question_and_answer, name='q_and_a'),

]
