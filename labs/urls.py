from django.urls import path
from . import views

app_name = 'labs'

urlpatterns = [
    path('tests/add/<str:kode_batch>/', views.labtest_create, name='labtest_create'), 
]