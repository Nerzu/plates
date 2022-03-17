from .models import Node
from django.forms import ModelForm, TextInput, Textarea


class NodeForm(ModelForm):
    class Meta:
        model = Node
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