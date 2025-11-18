from django.urls import path
from authentication.views import *
from farms.views import create_farm, edit_farm, delete_farm

app_name = 'farms'

urlpatterns = [
    # path('register/', register_view, name='register'),
    path("create/", create_farm, name="create_farm"),
    path("<int:id>/edit/", edit_farm, name="edit_farm"),
    path("<int:id>/delete/", delete_farm, name="delete_farm"),
]
