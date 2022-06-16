import json
import pyotp
import random
import requests
import re
import cryptocode
import os
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

from .aes_crypto import AESCipher
import hashlib


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
    if request.method == 'GET':
        user_uid = request.user.id
        notes = {}
        response = requests.get(f'http://84.38.180.103:10003/api/notes?user_uuid={user_uid}')
        if response:
            result = re.findall('{[^{}]*}', response.text)
            for i in range(0, len(result)):
                response_dict = json.loads(result[i])
                keys_merge = "".join(response_dict)
                user = User.objects.filter(pk=user_uid).get()
                aes_key = user.aes_pass
                aes = AESCipher(aes_key)
                if "uuidheaderbodyuser_uuid" in keys_merge:
                    note = {}
                    for key in response_dict:
                        if "uuid" == key:
                            note["id"] = response_dict[key]
                        if "header" == key:
                            note["title"] = response_dict[key]
                        if "body" in key:
                            note["number_piece"] = response_dict[key][0]
                            note["message_hash"] = response_dict[key][1:33]
                            note["text"] = response_dict[key][33:]
                    if note["message_hash"] in notes:
                        if note["number_piece"] == "1":
                            text = note["text"] + notes[note["message_hash"]]["text"]
                            decrypted_text = aes.decrypt(text)
                            notes[note["message_hash"]]["text"] = decrypted_text
                            notes[note["message_hash"]]["uuid_piece_1"] = note["id"]
                        else:
                            text = notes[note["message_hash"]]["text"] + note["text"]
                            decrypted_text = aes.decrypt(text)
                            notes[note["message_hash"]]["text"] = decrypted_text
                            notes[note["message_hash"]]["uuid_piece_2"] = note["id"]
                    else:
                        notes[note["message_hash"]] = {}
                        notes[note["message_hash"]]["text"] = note["text"]
                        notes[note["message_hash"]]["title"] = note["title"]
                        if note["number_piece"] == "1":
                            notes[note["message_hash"]]["uuid_piece_1"] = note["id"]
                        else:
                            notes[note["message_hash"]]["uuid_piece_2"] = note["id"]
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
        aes_password = os.urandom(32)
        if form.is_valid():
            form.save()
            if request.user.is_authenticated:
                return redirect('home')
            user = User.objects.filter(username=user_name).first()
            user.secret_key = secret_key
            user.aes_pass = aes_password
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
    try:
        del request.session
    except KeyError:
        pass
    return render(request, 'registration/logged_out.html')

@csrf_exempt
def key_ssl(request):

    if request.method == 'GET':
        session_key = random.getrandbits(256)
        private_key = random.getrandbits(256)
        cache.set('key_cache', private_key)
        A = pow(settings.G, private_key, settings.P)

        print(f"session_key = {session_key}\nprivate_key = {private_key}\nA = {A}")
        print(f"settings.P = {settings.P}")
        print(f"len pricate_key={len(str(private_key))}")
        response = {'p': str(settings.P),
            'g': str(settings.G),
            'A': str(A),
            }
        return JsonResponse(response)

    elif request.method == 'POST':
        json_body = json.loads(request.body)

        key_client_partitial = int(json_body['key_client'])
        msg_title = str(json_body['title'])
        msg_text = str(json_body['text'])
        print(f"title:{msg_title}\ntext:{msg_text}")

        private_key_cache = cache.get('key_cache')

        print(f"key_client: {type(key_client_partitial)}\nkey_part_client:{key_client_partitial}")
        key_full = pow(key_client_partitial, private_key_cache, settings.P)
        print(key_full)
        if key_full:
            print('Session key is correct')
            request_data = {'header': msg_title, 'body': msg_text, 'user_uuid': "b545d618-ff44-4319-9c88-2100d9928f32"}
            data = json.dumps(request_data, indent=2).encode('utf-8')
            response = requests.post('http://84.38.180.103:10003/api/notes', data)
            return redirect('home')
        else:
            print('Session key dont set')
            return redirect('home')

@csrf_exempt
def create(request):
#    print(request)
    error = ''
    if request.method == 'POST': #здесь отправляем на сервак заметку
        user_uid = request.user.id
        #user_uid = "b545d618-ff44-4319-9c88-2100d9928f32"
        print("User uid is:")
        print(user_uid)
        # json_body = json.loads(request.body)
        # print(str(json_body))
        form = NoteForm(request.POST)
        # form.title=json_body["iv"]
        # form.text=json_body["cipher"]
        # form.save()

        if form.is_valid():
#            form.save()
            form.save2(user_uid)
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

def edit(request, id1, id2):
    user_uid = request.user.id
    try:
#        response_piece_1 = requests.get(f'http://127.0.0.1:10003/api/notes/{id1}')
        response_piece_1 = requests.get(f'http://84.38.180.103:10003/api/notes/{id1}')
#        response_piece_2 = requests.get(f'http://127.0.0.1:10003/api/notes/{id2}')
        response_piece_2 = requests.get(f'http://84.38.180.103:10003/api/notes/{id2}')
        note = {}
        for response in [response_piece_1, response_piece_2]:
            print(response.text)
            result = re.findall('{[^{}]*}', response.text)
            response_dict = json.loads(result[0])
#            keys_merge = "".join(response_dict)
#           if "uuidheaderbodyuser_uuid" in keys_merge:
            if response == response_piece_1:
                text = ""
                for key in response_dict:
                    if "uuid" == key:
                        note["uuid_piece_1"] = response_dict[key]
                    if "header" in key:
                        note["title"] = response_dict[key]
                    if "body" in key:
                        note["message_hash"] = response_dict[key][1:33]
                        text = response_dict[key][33:] + text

            else:
                for key in response_dict:
                    if "uuid" == key:
                        note["uuid_piece_2"] = response_dict[key]
                    if "body" in key:
                        text = text + response_dict[key][33:]

        user = User.objects.filter(pk=user_uid).get()
        aes_key = user.aes_pass
        aes = AESCipher(aes_key)
        note["text"] = aes.decrypt(text)
        if request.method == 'POST':
            title = request.POST['title']
            text = request.POST['text']
            aes = AESCipher(aes_key)
            encrypted_text = aes.encrypt(text)
            len_message = len(encrypted_text)
            # hash_value = hashlib.sha256()
            # hash_value.update(bytes("{}".format(title), encoding="ascii"))
            # hash_value.update(bytes("{}".format(encrypted_text), encoding="ascii"))
            hash_value = hashlib.md5(bytes("{}{}".format(title, encrypted_text), encoding="ascii")).hexdigest()
            #print("The len of hash value is {}".format(len(hash_value)))
            # print("The digest_size of hash value is {}".format(hash_value.digest_size))
            #print("The hash value is {}".format(hash_value))
            ###################################################################
            # Тело сообщения состоит из метки части, хэш-значения сообщения (используется для однозначной идентификации сообщения)
            # и половине шифрованного телап сообщения)
            #####################################################################################################################
            message_1 = "1" + str(hash_value) + encrypted_text[:len_message // 2]
            message_2 = "2" + str(hash_value) + encrypted_text[len_message // 2:]
            for message in [message_1, message_2]:
#                print("The {} is \n{}".format((lambda x: "message 1" if message == message_1 else "message 2")(message),message))

                request_data = {'header': title, 'body': message}
                data = json.dumps(request_data, indent=2).encode('utf-8')
                if message == message_1:
#                    response = requests.patch(f'http://127.0.0.1:10003/api/notes/{id1}', data)
                    response = requests.patch(f'http://84.38.180.103:10003/api/notes/{id1}', data)
                else:
#                    response = requests.patch(f'http://127.0.0.1:10003/api/notes/{id2}', data)
                    response = requests.patch(f'http://84.38.180.103:10003/api/notes/{id2}', data)
            return redirect('home')
        else:
            return render(request, "main/edit.html", {"note": note})
    except Note.DoesNotExist:
        return redirect('home')

def delete(request, id1, id2):
    try:
#        note = Note.objects.get(id=id)
#        note.delete()
        for id in [id1, id2]:
#            response = requests.delete(f'http://127.0.0.1:10003/api/notes/{id}')
            response = requests.delete(f'http://84.38.180.103:10003/api/notes/{id}')
        return redirect('home')
    except Note.DoesNotExist:
        return redirect('home')

class SignUp(CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy("login")
    template_name = "registration/signup.html"
