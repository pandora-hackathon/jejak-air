from django.db import models
from batches.models import Activity, HarvestBatch
from profiles.models import UserProfile
from farms.models import City
from farms.utils import recalculate_farm_risk
from batches.utils import recalculate_batch_risk

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
        limit_choices_to={"user__role": "labAssistant"}, # hanya QC/labAssistant yang bisa input
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
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        # setelah LabTest tersimpan, hitung ulang risiko farm & batch
        farm = self.batch.farm
        recalculate_farm_risk(farm)
        recalculate_batch_risk(self.batch)

        # buat activity UJI_LAB
        lokasi_lab = self.lab.nama if self.lab else "Laboratorium"
        pelaku_qc = self.qc.user.get_full_name() or self.qc.user.username

        Activity.objects.create(
            batch=self.batch,
            tanggal=self.tanggal_uji,
            jenis="UJI_LAB",
            lokasi=lokasi_lab,
            pelaku=pelaku_qc,
            keterangan=f"Uji Cs-137: {self.nilai_cs137} Bq/kg"
            + (f" (batas {self.batas_aman_cs137} Bq/kg)" if self.batas_aman_cs137 else ""),
        )

        # Kalau risk_score PASS dan belum ada SIAP_EKSPOR, buat otomatis
        batch = self.batch
        if batch.risk_score is not None and batch.risk_score < 70:
            sudah_siap = batch.activities.filter(jenis="SIAP_EKSPOR").exists()
            if not sudah_siap:
                Activity.objects.create(
                    batch=batch,
                    tanggal=self.tanggal_uji,
                    jenis="SIAP_EKSPOR",
                    lokasi=lokasi_lab,
                    pelaku=pelaku_qc,
                    keterangan="Batch dinyatakan siap ekspor (risk score < 70)",
                )