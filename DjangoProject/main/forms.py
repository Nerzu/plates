import requests
import json
from .aes_crypto import AESCipher
import hashlib

from .models import Note, User, TwoFactor
from django import forms
from django.forms import ModelForm, TextInput, Textarea, PasswordInput
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm



class UserLoginForm(AuthenticationForm):
    username = forms.CharField(widget=TextInput(attrs={'class': 'form-control py-4', 'placeholder': 'Введите имя пользователя'}))
    password = forms.CharField(widget=PasswordInput(attrs={'class': 'form-control py-4', 'placeholder': 'Введите пароль пльзователя'}))
    # pin = forms.CharField(widget=PasswordInput(attrs={'class': 'form-control py-4', 'placeholder': 'Код из гугл аутентикатора'}))

    class Meta:
        model = User
        fields = ("username", "password")

class UserSignUpForm(UserCreationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Введите имя пользователя'}))
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Введите пароль'}))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Повторите пароль'}))

    class Meta:
        model = User
        fields = ('username', 'password1', 'password2')

class TwoFactorForm(ModelForm):
    pin_code = forms.CharField(widget=PasswordInput(attrs={'class': 'form-control py-4', 'placeholder': 'Код из гугл аутентикатора'}))

    class Meta:
        model = TwoFactor
        fields = ('pin_code',)

class NoteForm(ModelForm):
    class Meta:
        model = Note
        fields = ["title", "text"]
        widgets = {
            "title": TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите название'
            }),
            "text": Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Введите содержание'
            })
        }

    def save2(self, user_uid):
        key = 'Sixteen byte key'
        aes = AESCipher(key)
        cleaned_data = self.cleaned_data
        title = cleaned_data["title"]
        text = cleaned_data["text"]
        encrypted_text = aes.encrypt(text)
        #print(title)
        #print(encrypted_text)
        len_message = len(encrypted_text)
        #hash_value = hashlib.sha256()
        #hash_value.update(bytes("{}".format(title), encoding="ascii"))
        #hash_value.update(bytes("{}".format(encrypted_text), encoding="ascii"))
        hash_value = hashlib.md5(bytes("{}{}".format(title, encrypted_text), encoding="ascii")).hexdigest()
        #print("The len of hash value is {}".format(len(hash_value)))
        #print("The digest_size of hash value is {}".format(hash_value.digest_size))
        #print("The hash value is {}".format(hash_value))
        ###################################################################
        #Тело сообщения состоит из метки части, хэш-значения сообщения (используется для однозначной идентификации сообщения)
        # и половине шифрованного телап сообщения)
        #####################################################################################################################
        message_1 = "1" + str(hash_value) + encrypted_text[:len_message//2]
        message_2 = "2" + str(hash_value) + encrypted_text[len_message // 2:]
        for message in [message_1, message_2]:
            print("The {} is \n{}".format((lambda x: "message 1" if message == message_1 else "message 2")(message), message))

            request_data = {'header': title, 'body': message, 'user_uuid': str(user_uid)}
            #print(request_data)
            data = json.dumps(request_data, indent=2).encode('utf-8')
#            response = requests.post('http://127.0.0.1:10003/api/notes', data)
            response = requests.post('http://84.38.180.103:10003/api/notes', data)
