from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.urls import reverse_lazy
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.views.generic.edit import CreateView
from .models import Note
from .forms import NoteForm
from django.views import View
import pyotp
import time
from . import models


@login_required
def index(request):
    if request.method == 'GET':
        notes = Note.objects.all()
        return render(request, 'main/index.html', {'title': 'Главная страница сайта', 'notes': notes})
    elif request.method == 'POST':
        return render(request, 'main/index.html', {'title': 'Главная страница сайта'})


def about(request):
    return render(request, 'main/about.html')

def login(request):
    return render(request, 'registration/login.html')

def logout(request):
    return render(request, 'registration/logged_out.html')
#This is the comment
def create(request):
    error = ''
    if request.method == 'POST': #здесь отправляем на сервак заметку
        form = NoteForm(request.POST)
        if form.is_valid():
            #form.save2()
            form.getnote("b545d618-ff44-4319-9c88-2100d9928f32")
            # string = form.title + ';' + form.text
            return redirect('home')
        else:
            error = 'Форма была не верной'

    form = NoteForm()
    context ={
        'form': form,
        'error': error
    }
    return render(request, 'main/create.html', context)

def create_user(request):
    error = ''
    if request.method == 'POST':
        user = User.objects.create_user('myusernameme', 'myemail@crazymail.com', 'mypassword')
        user.first_name = 'John'
        user.last_name = 'Citizen'
        user.save()
        return redirect('home')

class SignUp(CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy("login")
    template_name = "registration/signup.html"

#Get from https://pyauth.github.io/pyotp/
def set_key(request):
    totp = pyotp.TOTP('base32secret3232')
    totp.now() # => '492039'
    # OTP verified for current time
    totp.verify('492039') # => True
    time.sleep(30)
    totp.verify('492039') # => False

class AuthCheckView(View):
    def get(self, request, pin):
        auth_info_detail = models.AuthInformation.objects.first()
        secret_key = auth_info_detail.secret_key
        totp = pyotp.TOTP(secret_key)
        print("Current OTP ", totp.now)
        verification_status = totp.verify(pin)
        if verification_status:
            notes = Note.objects.all()
            return render(request, 'main/index.html', {'title': 'Главная страница сайта', 'notes': notes})
        return render(request, 'main/index.html', {'title': 'Главная страница сайта'})
