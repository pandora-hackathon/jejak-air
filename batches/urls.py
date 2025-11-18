# batches/urls.py
from django.urls import path
from . import views

app_name = "batches"

urlpatterns = [
    path("", views.batch_list, name="batch_list"),
    path("<int:pk>/", views.batch_detail, name="batch_detail"),
    path("add/", views.batch_create, name="batch_create"),
    path("<int:pk>/edit/", views.batch_update, name="batch_update"),
    path("<int:pk>/delete/", views.batch_delete, name="batch_delete"),
]
