from django.urls import path, include
from . import views


urlpatterns = [
<<<<<<< Updated upstream
    path('', views.index, name='home'),
=======
    path('', views.index, name="home"),
    # path('home/<int:pin>', views.AuthCheckView.as_view(), name="home"),
>>>>>>> Stashed changes
    path('about', views.about, name='about'),
    path('create', views.create, name='create_note'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('main/login/', views.login, name='login_my'),
    path('accounts/logout/', views.logout, name='logout'),
    # path("signup/", views.SignUp.as_view(), name="signup"),
    path("signup/", views.register, name="signup"),
]