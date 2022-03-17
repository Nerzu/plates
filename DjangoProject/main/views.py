from django.shortcuts import render, redirect
from .models import Node
from .forms import NodeForm


def index(request):
    nodes = Node.objects.all()
    return render(request, 'main/index.html', {'title': 'Главная страница сайта', 'nodes': nodes})


def about(request):
    return render(request, 'main/about.html')

def create(request):
    error = ''
    if request.method == 'POST':
        form = NodeForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')
        else:
            error = 'Форма была не верной'

    form = NodeForm()
    context ={
        'form': form,
        'error': error
    }
    return render(request, 'main/create.html', context)