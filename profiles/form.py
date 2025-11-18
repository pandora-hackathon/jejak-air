from django import forms
from .models import UserProfile


class OwnerProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['full_name', 'number_phone']


# class LabAssistantProfileForm(forms.ModelForm):
#     class Meta:
#         model = UserProfile
#         fields = ['full_name', 'number_phone', 'laboratory']
