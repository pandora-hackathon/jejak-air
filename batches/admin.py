from django.contrib import admin
from .models import HarvestBatch, Activity, Commodity

# Register your models here.
admin.site.register(HarvestBatch)
admin.site.register(Activity)
admin.site.register(Commodity)