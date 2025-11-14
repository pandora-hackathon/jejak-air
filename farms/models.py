import uuid
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

class City(models.Model):
    name = models.CharField(max_length=100)
    province = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Farm(models.Model):
    name = models.CharField(max_length=50)
    city = models.ForeignKey(City, on_delete=models.CASCADE, null=True)
    location = models.CharField(max_length=100)
    risk_score = models.PositiveIntegerField(validators=[MinValueValidator(0), MaxValueValidator(100)],
                default=30,  )

    def __str__(self):
        return self.name
