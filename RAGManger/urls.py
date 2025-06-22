from django.urls import path, re_path
from .views import upload_RAG_content, sse_notifications, notifications_view,get_RAG_content_from_db

app_name = 'RAGManger'

urlpatterns = [
    path('upload/', upload_RAG_content, name='upload_RAG_content'),
    path('sse-notifications/', sse_notifications, name='sse_notifications'),
    path('notifications/', notifications_view, name='notifications_view'),
    path('get_RAG_content/', get_RAG_content_from_db, name='get_RAG_content_from_db'),
    
]