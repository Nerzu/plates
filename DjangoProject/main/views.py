from django.shortcuts import render, redirect
from .models import Note
from .forms import NoteForm


def index(request):
    notes = Note.objects.all()
    return render(request, 'main/index.html', {'title': 'Главная страница сайта', 'notes': notes})


def about(request):
    return render(request, 'main/about.html')

def login(request):
    return render(request, 'registration/login.html')

def logout(request):
    return render(request, 'registration/logged_out.html')

def create(request):
    error = ''
    if request.method == 'POST': #здесь отправляем на сервак заметку
        form = NoteForm(request.POST)
        if form.is_valid():
            form.save()
            string = form.title + ';' + form.text
            return redirect('home')
        else:
            error = 'Форма была не верной'

    form = NoteForm()
    context ={
        'form': form,
        'error': error
    }
    return render(request, 'main/create.html', context)

from django.contrib.auth.models import User

def create_user(request):
    error = ''
    if request.method == 'POST':
        user = User.objects.create_user('myusernameme', 'myemail@crazymail.com', 'mypassword')
        user.first_name = 'John'
        user.last_name = 'Citizen'
        user.save()
        return redirect('home')

def RegisterUser(request):
    # form_class = UserCreatioForm
    # template_name = "main/register.html"
    # success_url = reverse_lazy('login')
    #
    # def get_content_data(self, *, object_list=None, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     c_def = self.get_user_context(title="Регистрация")
    #     return dict(list(context.items()) + list(c_def.items()))
    return render(request, 'main/register.html')
