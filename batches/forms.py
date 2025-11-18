# batches/forms.py
from django import forms
from .models import HarvestBatch, Activity
from farms.models import Farm


class HarvestBatchForm(forms.ModelForm):
    class Meta:
        model = HarvestBatch
        fields = [
            "farm",
            "commodity",
            "tanggal_tebar",
            "tanggal_panen",
            "volume_kg",
            "tujuan",
        ]
        widgets = {
            "tanggal_tebar": forms.DateInput(attrs={"type": "date"}),
            "tanggal_panen": forms.DateInput(attrs={"type": "date"}),
        }

    def __init__(self, *args, **kwargs):
        # kita kirim user dari view, supaya bisa filter farm
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        # default: jangan kasih farm apa-apa dulu
        self.fields["farm"].queryset = Farm.objects.none()

        if user is not None and hasattr(user, "profile"):
            # hanya farm yang owner-nya = user ini
            self.fields["farm"].queryset = Farm.objects.filter(owner=user.profile)

class ActivityManualForm(forms.ModelForm):
    class Meta:
        model = Activity
        fields = ["tanggal", "lokasi", "pelaku", "keterangan"]
        widgets = {
            "tanggal": forms.DateInput(attrs={"type": "date"}),
        }
