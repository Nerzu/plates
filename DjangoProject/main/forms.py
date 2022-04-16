import requests
import json

from .models import Note
from django.forms import ModelForm, TextInput, Textarea


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