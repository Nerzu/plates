<<<<<<< Updated upstream
=======
# from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractUser
>>>>>>> Stashed changes
from django.db import models

# Create your models here.
class User(AbstractUser):
    secret_key = models.CharField(max_length=255)
    image = models.ImageField(upload_to='users_images', blank=True)

class Note(models.Model):
    title = models.CharField('Название', max_length=50)
    text = models.TextField('Содержание')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Заметка'
<<<<<<< Updated upstream
        verbose_name_plural = 'Заметки'
=======
        verbose_name_plural = 'Заметки'

>>>>>>> Stashed changes
