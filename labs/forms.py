# labs/forms.py
from django import forms
from .models import Laboratory, LabTest
from profiles.models import UserProfile

class LaboratoryForm(forms.ModelForm):
    class Meta:
        model = Laboratory
        fields = ['nama', 'city']

class LabTestForm(forms.ModelForm):
    class Meta:
        model = LabTest
        fields = ['nilai_cs137', 'tanggal_uji', 'lab']
        widgets = {
            'tanggal_uji': forms.DateInput(attrs={'type': 'date'}),
        }
    
    qc = forms.ModelChoiceField(
        queryset=UserProfile.objects.filter(user__role='labAssistant'),
        required=True,
        widget=forms.HiddenInput()
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['qc'].widget = forms.HiddenInput()