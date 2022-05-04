import json
import pyotp
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.edit import CreateView

from .forms import NoteForm, UserLoginForm, TwoFactorForm
from .forms import UserSignUpForm
from .models import Note, User


def check_pin_google(pin, secret_key):
    totp = pyotp.TOTP(secret_key)
    verification_status = totp.verify(pin)
    if verification_status:
        return True
    else:
        return False

# def index(request):
#     notes = Note.objects.all()
#     return render(request, 'main/index.html', {'title': 'Главная страница сайта', 'notes': notes})

class DH_Endpoint():
   def __init__(self, public_key1, public_key2, private_key):
       self.public_key1 = public_key1
       self.public_key2 = public_key2
       self.private_key = private_key
       self.full_key = None

   def generate_partial_key(self):
       partial_key = self.public_key1 ** self.private_key
       partial_key = partial_key % self.public_key2
       return partial_key

   def generate_full_key(self, partial_key_r):
       full_key = partial_key_r ** self.private_key
       full_key = full_key % self.public_key2
       self.full_key = full_key
       return full_key

   def encrypt_message(self, message):
       encrypted_message = ""
       key = self.full_key
       for c in message:
           encrypted_message += chr(ord(c) + key)
       return encrypted_message

   def decrypt_message(self, encrypted_message):
       decrypted_message = ""
       key = self.full_key
       for c in encrypted_message:
           decrypted_message += chr(ord(c) - key)
       return decrypted_message



@login_required(login_url='login_my')
def index(request):
    print(request)
    if request.method == 'GET':
        notes = Note.objects.all()
        return render(request, 'main/index.html', {'title': f'Главная страница сайта', 'notes': notes})
    elif request.method == 'POST':
        return render(request, 'main/index.html', {'title': 'Главная страница сайта'})

def about(request):
    print(request)
    form = NoteForm()
    context = {
        'form': form,
    }
    return render(request, 'main/about.html', context)

def register(request):
    if request.method == 'POST':
        form = UserSignUpForm(data=request.POST)
        user_name = request.POST.get('username')
        secret_key = pyotp.random_base32()
        if form.is_valid():
            form.save()
            if request.user.is_authenticated:
                return redirect('home')
            user = User.objects.filter(username=user_name).first()
            user.secret_key = secret_key
            user.save(update_fields=['secret_key'])
            return render(request, 'registration/show_code.html', {'show_code_text': secret_key})
        else:
            return render(request, 'registration/signup.html', {'form': form})
    else:
        if request.user.is_authenticated:
            return redirect('home')
        form_class = UserSignUpForm()
        return render(request, 'registration/signup.html', {'form': form_class})

def login(request):
    if request.method == 'POST':
        print('hello')
        form = UserLoginForm(data=request.POST)
        if form.is_valid():
            username = request.POST['username']
            password = request.POST['password']
            user = auth.authenticate(username=username, password=password)
            if user and user.is_active:
                request.session['pk'] = user.pk
                return redirect('twofactor')
            else:
                return render(request, 'registration/login.html', {'form': form})
        else:
            return render(request, 'registration/login.html', {'form': form})
    else:
        form = UserLoginForm()
        context = {'form': form}
        return render(request, 'registration/login.html', context)

def check_pin_code(request):
    if request.method == 'POST':
        form = TwoFactorForm(request.POST or None)
        pk = request.session.get('pk')
        if pk:
            user = User.objects.get(pk=pk)
            secret_key = user.secret_key
            pin = request.POST['pin_code']
            if form.is_valid():
                totp = pyotp.TOTP(secret_key)
                verification_status = totp.verify(pin)
                if verification_status:
                    auth.login(request, user)
                    return redirect('home')
                else:
                    return redirect('twofactor')
            else:
                return redirect('twofactor')
        else:
            return redirect('login_my')
    else:
        form = TwoFactorForm
        context = {'form': form}
        return render(request, 'registration/twofactor.html', context)

def logout(request):
    return render(request, 'registration/logged_out.html')

@csrf_exempt
def key_ssl(request):


    # key_client = json.loads(request.body)
    #
    # print(key_client)
    print(request.method)
    if request.method == 'GET':
        print(request.GET['client_partial'])
        print('123213')
        response = {
            'is_key': 123456789
        }
        return JsonResponse(response)

    if request.method == 'GET':
        key = {'key': '1111111111111'}

        json_data = json.dumps(key)


        return json_data

    elif request.method == 'POST':
        json_body = json.loads(request.body)
        print(json_body)

@csrf_exempt
def create(request):
    print(request)
    error = ''
    if request.method == 'POST': #здесь отправляем на сервак заметку

        # json_body = json.loads(request.body)
        # print(str(json_body))
        form = NoteForm(request.POST)
        # form.title=json_body["iv"]
        # form.text=json_body["cipher"]
        # form.save()

        if form.is_valid():
            form.save()
            #form.save2()
            # form.getnote("b545d618-ff44-4319-9c88-2100d9928f32")
            # string = form.title + ';' + form.text
            # return redirect('home')
        else:
            error = 'Форма была не верной'

    form = NoteForm()
    context ={
        'form': form,
        'error': error
    }
    return render(request, 'main/create.html', context)

def edit(request, id):
    try:
        note = Note.objects.get(id=id)
        if request.method == 'POST':
            note.title = request.POST['title']
            note.text = request.POST['text']
            note.save()
            return redirect('home')
        else:
            return render(request, "main/edit.html", {"form": note})
    except Note.DoesNotExist:
        return redirect('home')

def delete(request, id):
    try:
        note = Note.objects.get(id=id)
        note.delete()
        return redirect('home')
    except Note.DoesNotExist:
        return redirect('home')

class SignUp(CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy("login")
    template_name = "registration/signup.html"