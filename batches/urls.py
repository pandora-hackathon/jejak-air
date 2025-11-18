# batches/urls.py
from django.urls import path
from . import views

app_name = "batches"

urlpatterns = [
    path("", views.batch_list, name="batch_list"),
    path("create/", views.batch_create, name="batch_create"),

    path("<str:pk>/", views.batch_detail, name="batch_detail"),
    path("<str:pk>/edit/", views.batch_update, name="batch_update"),
    path("<str:pk>/delete/", views.batch_delete, name="batch_delete"),

    # aksi pengiriman
    path("<str:pk>/ship/", views.batch_mark_shipped, name="batch_mark_shipped"),
    path("<str:pk>/receive/", views.batch_mark_received, name="batch_mark_received"),

    # activity manual
    path("<str:pk>/activities/manual/", views.activity_manual_create,
         name="activity_manual_create"),
]
