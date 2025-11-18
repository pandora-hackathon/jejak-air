from django.urls import path
from . import views

app_name = 'labs'

urlpatterns = [
    path('', views.laboratory_list, name='laboratory_list'),
    path('add/', views.laboratory_create, name='laboratory_create'),
    path('<int:pk>/', views.laboratory_detail, name='laboratory_detail'),
    path('<int:pk>/delete/', views.laboratory_delete, name='laboratory_delete'),
    path('tests/add/<str:kode_batch>/', views.labtest_create, name='labtest_create'),
]