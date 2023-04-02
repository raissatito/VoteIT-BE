from django.urls import path
from .views import *

urlpatterns = [
    path('login', auth_login, name='login'),
    path('register', register, name='register'),
    path('get-user', get_username, name='get-user'),
]