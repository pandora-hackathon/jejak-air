from django.db import models
from batches.models import HarvestBatch
from profiles.models import UserProfile

# Create your models here.

class Laboratory(models.Model):
    nama = models.CharField(max_length=100)
    lokasi = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return self.nama

class TestParameter(models.Model):
    kode = models.CharField(max_length=50, unique=True)
    nama = models.CharField(max_length=100)
    satuan = models.CharField(max_length=20)
    batas_aman_default = models.FloatField()
    kategori = models.CharField(
        max_length=50,
        help_text="Contoh: Logam Berat, Mikrobiologi, Radioaktif",
    )
    keterangan = models.TextField(blank=True)

    def __str__(self):
        return f"{self.nama} ({self.satuan})"
    
class LabTest(models.Model):
    batch = models.ForeignKey(HarvestBatch, on_delete=models.CASCADE)
    parameter = models.ForeignKey(TestParameter, on_delete=models.PROTECT)

    nilai = models.FloatField()
    batas_aman = models.FloatField(
        null=True, blank=True,
        help_text="Jika kosong, akan memakai batas_aman_default dari parameter",
    )

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
        return f"{self.batch.kode_batch} - {self.parameter.nama} ({self.kesimpulan})"

    @property
    def lab(self):
        """Mengambil lab dari UserProfile QC."""
        # Menghindari error jika laboratory belum di-set di UserProfile
        return getattr(self.qc, "laboratory", None)