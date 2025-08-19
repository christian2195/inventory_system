# src/apps/users/urls.py
from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('perfil/', views.UserProfileView.as_view(), name='profile'),
    path('perfil/editar/', views.UserUpdateView.as_view(), name='update_profile'),
    path('registro/', views.UserRegisterView.as_view(), name='register'),
]