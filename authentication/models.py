import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('farmOwner', 'Farm Owner'),
        ('labAssistant', 'Lab Assistant'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=15, choices=ROLE_CHOICES, default='farmOwner')
    has_profile = models.BooleanField(default=False)

    def __str__(self):
        return self.username

