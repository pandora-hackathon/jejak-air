from django import forms
from django.forms import ModelForm
from farms.models import Farm, City

class CityForm(ModelForm):
    class Meta:
        model = City
        fields = ["name", "province", "code"]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500',
            }),
            'province': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500',
            }),
            'code': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500',
            }),
        }

class FarmForm(ModelForm):
    class Meta:
        model = Farm
        fields = ["name", "location", "risk_score"]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500',
            }),
            'location': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500',
            }),
            'risk_score': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500',
            }),
        }
