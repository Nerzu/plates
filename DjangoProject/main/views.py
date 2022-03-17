from django.shortcuts import render, redirect
from .models import Note
from .forms import NoteForm


def index(request):
    notes = Note.objects.all()
    return render(request, 'main/index.html', {'title': 'Главная страница сайта', 'notes': notes})


def about(request):
    return render(request, 'main/about.html')

def create(request):
    error = ''
    if request.method == 'POST': #здесь отправдяем на сервак заметку
        form = NoteForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')
        else:
            error = 'Форма была не верной'

    form = NoteForm()
    context ={
        'form': form,
        'error': error
    }
    return render(request, 'main/create.html', context)