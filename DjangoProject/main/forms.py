import requests
import json

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

    def save2(self):
        cleaned_data = self.cleaned_data
        title = cleaned_data["title"]
        text = cleaned_data["text"]
        print(title)
        print(text)
        request_data = {'header': title, 'body': text, 'user_uuid': "b545d618-ff44-4319-9c88-2100d9928f32"}
        data = json.dumps(request_data, indent=2).encode('utf-8')
        response = requests.post('http://0.0.0.0:10003/api/notes', data)
        print(response.text)

    def getnote(self,note_uuid):
        response = requests.get(f'http://0.0.0.0:10003/api/notes?user_uuid={note_uuid}')
        print(response.text)