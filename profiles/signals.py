from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings

from .models import UserProfile
from authentication.models import User


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Jika user baru dibuat → otomatis buat UserProfile kosong.
    """
    if created:
        UserProfile.objects.create(user=instance)
