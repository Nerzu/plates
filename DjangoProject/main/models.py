from django.contrib.auth.models import AbstractUser
from django.db import models
import json
import requests
import os

# Create your models here.
class User(AbstractUser):
    secret_key = models.CharField(max_length=255)
    image = models.ImageField(upload_to='users_images', blank=True)
    aes_pass = models.CharField(max_length=256)

class TwoFactor(models.Model):
    pin_code = models.CharField(max_length=6)

    def __str__(self):
        return self.pin_code


class Note(models.Model):
    title = models.CharField('Название', max_length=50)
    text = models.TextField('Содержание')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Заметка'
        verbose_name_plural = 'Заметки'