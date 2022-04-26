from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
# from .models import UserProfile

# Register your models here.
from .models import Note
from .models import User

admin.site.register(Note)
admin.site.register(User)
