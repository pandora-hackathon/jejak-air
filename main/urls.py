from . import views
from django.urls import path
from main.views import *

app_name = 'main'

urlpatterns = [
    path('', home, name='home'),
    path('dashboard/', views.dashboard_switcher, name='dashboard_switcher'), 
    path('dashboard/qc/', views.dashboard_qc, name='dashboard_qc'),
]
