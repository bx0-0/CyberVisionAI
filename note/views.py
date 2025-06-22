from django.shortcuts import get_object_or_404, redirect, render
from .models import Notes
from  django.core.paginator import Paginator 
from .forms import NotesForm
from django.contrib.auth.decorators import login_required

@login_required
def list_notes(request):
    notes = Notes.objects.filter(user = request.user).order_by('-updated_at')
    paginator = Paginator(notes, 3)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'show_notes.html', {'notes': page_obj})

@login_required
def create_note(request):
    if request.method == 'POST':
        my_form = NotesForm(request.POST)
        if my_form.is_valid():
            new_note = my_form.save(commit=False)
            new_note.user = request.user
            new_note.save()
            return redirect('notes:list_notes')    
    else:
        my_form = NotesForm()

    context = {'form': my_form}            
    return render(request, 'note_form.html', context)

@login_required
def delete_note(request, slug):
    note = get_object_or_404(Notes, slug=slug, user = request.user)
    note.delete()
    return redirect('notes:list_notes')

@login_required
def edit_note(request, slug):
    note = get_object_or_404(Notes, slug=slug, user = request.user)
    if request.method == 'POST':
        my_form = NotesForm(request.POST, instance=note)
        if my_form.is_valid():
            my_form.save()
            return redirect('notes:list_notes')    
    else:
        my_form = NotesForm(instance=note)

    context = {'form': my_form}            
    return render(request, 'note_form.html', context)
