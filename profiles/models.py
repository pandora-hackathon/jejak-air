
# Create your models here.
import uuid
from django.db import models
from django.conf import settings

class UserProfile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='profile'
    )

    picture = models.ImageField(upload_to='profile-picture/', null=True, blank=True)
    number_phone = models.CharField(max_length=15, null=True, blank=True)

    full_name = models.CharField(max_length=100, null=True, blank=True)

    laboratory = models.ForeignKey(
        'labs.Laboratory',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='lab_assistants'
    )

    def __str__(self):
        return f"Profile of {self.user.username}"

    def save(self, *args, **kwargs):
        if self.user.role != 'labAssistant':
            self.laboratory = None

        super().save(*args, **kwargs)

        if not self.user.has_profile:
            self.user.has_profile = True
            self.user.save(update_fields=['has_profile'])

    class Meta:
        verbose_name = "User Profile"
        verbose_name_plural = "User Profiles"
