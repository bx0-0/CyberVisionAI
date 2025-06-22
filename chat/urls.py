from django.urls import path
from .views import streamlit_view,send_api,save_chat,get_conversation,list_conversations,delete_conversation,create_mind_map,mind_map_view,search_page,search_LLm

app_name='chat'
urlpatterns = [
    path('x/', streamlit_view, name='streamlit_view'),
    path('send_api/', send_api, name='send_api'),
    path('save_chat/', save_chat, name='save_chat'),
    path('list_conversations/', list_conversations, name='list_conversations'),
    path('create_mind_map/', create_mind_map, name='create_mind_map'),
    path('show_mind_map/<slug:slug>/', mind_map_view, name='mind_map_view'),
    path('show_conversations/<slug>/', get_conversation, name='get_conversation'),
    path('delete_conversation/<slug>/', delete_conversation, name='delete_conversation'),
    path('researcher/', search_LLm, name='researcher_LLm'),
    path('search/', search_page, name='search_page'),

]

