from django.urls import path, include
from . import views


urlpatterns = [
    path('', views.index, name='home'),
    # path('home/<int:pin>', views.AuthCheckView.as_view(), name="home"),
    path('about', views.about, name='about'),
    path('create', views.create, name='create_note'),
    path('edit/<int:id>', views.edit, name='edit_note'),
    path('delete/<int:id>', views.delete, name='delete_note'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('main/login/', views.login, name='login_my'),
    path('main/twofactor/', views.check_pin_code, name='twofactor'),
    path('accounts/logout/', views.logout, name='logout'),
    # path("signup/", views.SignUp.as_view(), name="signup"),
    path("signup/", views.register, name="signup"),
    path("twofactor/", views.check_pin_code, name="twofactor"),
    # path("signup/code/", views.check_pin_code, name="twofactor"),
]