from django.urls import path, include
from . import views


urlpatterns = [
    path('', views.index, name="home"),
    path('home/<int:pin>', views.AuthCheckView.as_view(), name="home"),
    path('about', views.about, name='about'),
    path('create', views.create, name='create_note'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('accounts/login/', views.login, name='login'),
    path('accounts/logout/', views.logout, name='logout'),
    path("signup/", views.SignUp.as_view(), name="signup"),
]