from .models import Note
from .models import User
from django import forms
from django.forms import ModelForm, TextInput, Textarea, PasswordInput
from django.contrib.auth.forms import AuthenticationForm

class UserLoginForm(AuthenticationForm):
    username = forms.CharField(widget=TextInput(attrs={'class': 'form-control py-4', 'placeholder': 'Введите имя пользователя'}))
    password = forms.CharField(widget=PasswordInput(attrs={'class': 'form-control py-4', 'placeholder': 'Введите пароль пльзователя'}))
    pin = forms.CharField(widget=PasswordInput(attrs={'class': 'form-control py-4', 'placeholder': 'Код из гугл аутентикатора'}))


    class Meta:
        model = User
        fields = ("username", "password", "pin")

class UserSignUpForm(AuthenticationForm):
    class Meta:
        model = User

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
        