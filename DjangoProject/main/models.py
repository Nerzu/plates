from django.contrib.auth.models import User
from django.db import models

# Create your models here.


class Note(models.Model):
    title = models.CharField('Название', max_length=50)
    text = models.TextField('Содержание')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Заметка'
        verbose_name_plural = 'Заметки'

class AuthInformation(models.Model):
    secret_key = models.CharField(max_length=255)
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"AuthInfo - {self.user}"

    # class Meta:
    #     verbose_name = 'Key'
    #     verbose_name_plural = 'Keys'