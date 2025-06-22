from django.urls import path
from .views import  list_notes, create_note, delete_note, edit_note

app_name = 'note'

urlpatterns = [
    path('list', list_notes, name='list_notes'),
    path('create_note', create_note, name='create_note'),
    path('delete_note/<slug>', delete_note, name='delete_note'),
    path('edit_note/<slug>', edit_note, name='edit_note'),
]