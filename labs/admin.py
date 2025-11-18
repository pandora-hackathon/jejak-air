from django.contrib import admin
from .models import Laboratory, LabTest

# Register your models here.
admin.site.register(Laboratory)
admin.site.register(LabTest)