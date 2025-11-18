import uuid
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

from profiles.models import UserProfile

class City(models.Model):
    name = models.CharField(max_length=100)
    province = models.CharField(max_length=100)
    code = models.CharField(max_length=10, unique=True, help_text="Kode singkat kota, misal IDM untuk Indramayu")

    def __str__(self):
        return self.name

class Farm(models.Model):
    name = models.CharField(max_length=50)
    city = models.ForeignKey(City, on_delete=models.CASCADE, null=True)
    location = models.CharField(max_length=100)
    risk_score = models.PositiveIntegerField(validators=[MinValueValidator(0), MaxValueValidator(100)], default=30)
    owner = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name="farms", limit_choices_to={"user__role": "farmOwner"})

    def __str__(self):
        return self.name
