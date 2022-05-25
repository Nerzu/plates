import json
import pyotp
import random
import requests
import re
import cryptocode
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

from django.conf import settings
from django.core.cache import cache
from django.views.generic.base import TemplateView

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
       # full_key = partial_key_r ** self.private_key
       # full_key = full_key % self.public_key2
       full_key  = pow(partial_key_r, self.private_key, self.public_key2)
       self.full_key = full_key
       return full_key

   def encrypt_message(self, message):
       encrypted_message = ""
       key = self.full_key
       for c in message:
           print(f'ord({c}):{ord(c) + key}')
           encrypted_message += chr(ord(c) + key)
       return encrypted_message

   def decrypt_message(self, encrypted_message):
       decrypted_message = ""
       key = self.full_key
       for c in encrypted_message:
           print(f'ord({c}):{ord(c) - key}')
           decrypted_message += chr(ord(c) - key)
       return decrypted_message



@login_required(login_url='login_my')
def index(request):
    if request.method == 'GET':
#         user_uid = request.user.id
#         # note = Note()
#         # note.print_note(user_uid)
#         notes = []
# #        response = requests.get(f'http://0.0.0.0:10003/api/notes?user_uuid={user_uid}')
#         response = requests.get(f'http://84.38.180.103:10003/api/notes?user_uuid={user_uid}')
# #        response = requests.get('http://127.0.0.1:53210')
#         if response:
#
#             result = re.findall('{[^{}]*}', response.text)
#             for i in range(0, len(result)):
#                 response_dict = json.loads(result[i])
#                 keys_merge = "".join(response_dict)
#                 print(keys_merge)
#                 if "uuidheaderbodyuser_uuid" in keys_merge:
#                     note = {}
#                     for key in response_dict:
#                         if "uuid" == key:
#                             note["id"] = response_dict[key]
#                         if "header" == key:
#                             note["title"] = response_dict[key]
#                         if "body" == key:
#                             note["text"] = response_dict[key]
#                 notes.append(note)
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

    if request.method == 'GET':
        session_key = random.getrandbits(256)
        private_key = random.getrandbits(256)
        cache.set('key_cache', private_key)
        A = pow(settings.G, private_key, settings.P)
        cache.set('server_partitial', A)

        print(f"session_key = {session_key}\nprivate_key = {private_key}\nA = {A}")
        print(f"settings.P = {settings.P}")
        print(f"len pricate_key={len(str(private_key))}")
        response = {'p': str(settings.P),
            'g': str(settings.G),
            'A': str(A),
            'session_key': str(session_key),
            }
        return JsonResponse(response)

    elif request.method == 'POST':
        json_body = json.loads(request.body)

        key_client_partitial = int(json_body['key_client'])
        key_client_full = int(json_body['key_full'])
        msg_title = str(json_body['title'])
        msg_enc = str(json_body['text'])
        print(f"title:{msg_title}\ntext:{msg_enc}")

        private_key_cache = cache.get('key_cache')
        server_key_partitial = cache.get('server_partitial')

        print(f"key_client: {type(key_client_partitial)}\nkey_part_client:{key_client_partitial}")
        key_full = pow(key_client_partitial, private_key_cache, settings.P)
        print(key_full)
        if key_full == key_client_full:
            print('Session key is correct')

            dh_class = DH_Endpoint(settings.G, settings.P, private_key_cache)
            dh_full_key = dh_class.generate_full_key(key_client_partitial)
            print(dh_full_key)
            str_msg = dh_class.decrypt_message(msg_enc)
            print(str_msg)

            request_data = {'header': msg_title, 'body': str_msg, 'user_uuid': "b545d618-ff44-4319-9c88-2100d9928f32"}
            data = json.dumps(request_data, indent=2).encode('utf-8')
            #        response = requests.post('http://0.0.0.0:10003/api/notes', data)
            # response = requests.post('http://84.38.180.103:10003/api/notes', data)

            return redirect('home')

        else:
            print('Session key dont set')
            return redirect('home')

@csrf_exempt
def create(request):
#    print(request)
    error = ''
    if request.method == 'POST': #здесь отправляем на сервак заметку

        # json_body = json.loads(request.body)
        # print(str(json_body))
        form = NoteForm(request.POST)
        # form.title=json_body["iv"]
        # form.text=json_body["cipher"]
        # form.save()

        if form.is_valid():
#            form.save()
            form.save2()
            # form.getnote("b545d618-ff44-4319-9c88-2100d9928f32")
            return redirect('home')
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
        #note = Note.objects.get(id=id)
#        response = requests.get(f'http://0.0.0.0:10003/api/notes/{id}')
        response = requests.get(f'http://84.38.180.103:10003/api/notes/{id}')
#        response = requests.get('http://127.0.0.1:53211')
        #note_dict = response.json()
        result = re.findall('{[^{}]*}', response.text)
        response_dict = json.loads(result[0])
        keys_merge = "".join(response_dict)
#        if "uuidheaderbodyuser_uuid" in keys_merge:
        note = {}
        for key in response_dict:
            if "uuid" == key:
                note["uuid"] = response_dict[key]
            if "header" == key:
                note["title"] = response_dict[key]
            if "body" == key:
                note["text"] = response_dict[key]
        if request.method == 'POST':
            title = request.POST['title']
            text = request.POST['text']
            # note.save()
            request_data = {'header': title, 'body': text}
            data = json.dumps(request_data, indent=2).encode('utf-8')
#            response = requests.patch(f'http://0.0.0.0:10003/api/{id}', data)
            response = requests.patch(f'http://84.38.180.103:10003/api/notes/{id}', data)
            return redirect('home')
        else:
            return render(request, "main/edit.html", {"note": note})
    except Note.DoesNotExist:
        return redirect('home')

def delete(request, id):
    try:
#        note = Note.objects.get(id=id)
#        note.delete()
#        response = requests.delete(f'http://0.0.0.0:10003/api/{id}')
        response = requests.delete(f'http://84.38.180.103:10003/api/notes/{id}')
        return redirect('home')
    except Note.DoesNotExist:
        return redirect('home')

class SignUp(CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy("login")
    template_name = "registration/signup.html"