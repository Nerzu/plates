from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
# from .models import UserProfile

# Register your models here.
from .models import Note
<<<<<<< Updated upstream

admin.site.register(Note)
=======
from .models import User
# from .models import AuthInformation
# #
# class UserInline(admin.StackedInline):
#     model = AuthInformation
#     can_delete = False
#     verbose_name_plural = 'Доп. информация'
# #
# class UserAdmin(UserAdmin):
#     inlines = (UserInline, )


# admin.site.unregister(User)
# admin.site.register(User, UserAdmin)

admin.site.register(Note)
admin.site.register(User)
# admin.site.register(AuthInformation)
>>>>>>> Stashed changes
