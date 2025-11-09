from django.db import models
from batches.models import HarvestBatch
from profiles.models import UserProfile
from farms.models import City

# Create your models here.

class Laboratory(models.Model):
    nama = models.CharField(max_length=100)
    city = models.ForeignKey(City, on_delete=models.CASCADE)

    def __str__(self):
        return self.nama

class LabTest(models.Model):
    batch = models.OneToOneField(HarvestBatch, on_delete=models.CASCADE, related_name='lab_test')
    nilai_cs137 = models.FloatField()
    batas_aman_cs137 = models.FloatField(null=True, blank=True)

    kesimpulan = models.CharField(
        max_length=20,
        help_text="AMAN / BERMASALAH",
    )

    tanggal_uji = models.DateField()

    qc = models.ForeignKey(
        UserProfile,
        on_delete=models.PROTECT,
        limit_choices_to={"role": "QC"}, # hanya QC yang bisa input
    )

    class Meta:
        ordering = ["tanggal_uji"]

    def __str__(self):
        return f"{self.batch.kode_batch} ({self.kesimpulan})"

    @property
    def lab(self):
        """Mengambil lab dari UserProfile QC."""
        # Menghindari error jika laboratory belum di-set di UserProfile
        return getattr(self.qc, "laboratory", None)