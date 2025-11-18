from django.urls import path
from authentication.views import *

app_name = 'profiles'

urlpatterns = [
    path('user/create-profile/', register_view, name='register'),
]
