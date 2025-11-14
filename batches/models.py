from datetime import timezone
from django.db import models
from farms.models import Farm

# Create your models here.

class HarvestBatch(models.Model):
    QUALITY_CHOICES = [
        ("AMAN", "Aman"),
        ("PENDING", "Dalam Pengecekan"),
        ("MASALAH", "Bermasalah"),
    ]

    farm = models.ForeignKey(Farm, on_delete=models.CASCADE, related_name="batches")
    kode_batch = models.CharField(max_length=50, unique=True)
    commodity = models.CharField(max_length=100) # udang, bandeng, rumput laut, dll.
    tanggal_tebar = models.DateField()
    tanggal_panen = models.DateField()
    volume_kg = models.FloatField()
    tujuan = models.CharField(max_length=100) 
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True) # negara / buyer

    quality_status = models.CharField(
        max_length=20,
        choices=QUALITY_CHOICES,
        default="PENDING",
    )

    # risk_score final (0–100), hasil kombinasi uji lab + farm risk
    risk_score = models.IntegerField(null=True, blank=True)

    # menandai apakah batch ini sudah benar-benar dikirim
    is_shipped = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.kode_batch

    @property
    def shipment_status(self) -> str:
        """
        - jika is_shipped = True -> SUDAH_DIKIRIM
        - jika risk_score belum ada -> BELUM_DITINJAU
        - jika risk_score < 70  -> LAYAK_KIRIM
        - jika risk_score >= 70 -> DITAHAN
        """
        if self.is_shipped:
            return "SUDAH_DIKIRIM"

        if self.risk_score is None:
            return "BELUM_DITINJAU"

        if self.risk_score < 70:
            return "LAYAK_KIRIM"
        return "DITAHAN"


class Activity(models.Model):
    ACTIVITY_CHOICES = [
        ("PENEBARAN", "Penebaran benur"),
        ("PANEN", "Panen"),
        ("DARI_TAMBAK", "Batch dibuat di tambak"),
        ("UJI_LAB", "Uji laboratorium"),
        ("SIAP_EKSPOR", "Disiapkan untuk ekspor"),
        ("DIEKSPOR", "Diekspor"),
        ("DITERIMA", "Diterima pihak tujuan"),
        ("LAINNYA", "Lainnya"),
    ]

    batch = models.ForeignKey(
        HarvestBatch,
        on_delete=models.CASCADE,
        related_name="activities",
    )

    tanggal = models.DateField()
    jenis = models.CharField(max_length=20, choices=ACTIVITY_CHOICES)

    lokasi = models.CharField(max_length=200)
    pelaku = models.CharField(max_length=100) # nama tambak/pabrik/kurir/lab, dll.
    keterangan = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["tanggal", "created_at"]

    def __str__(self):
        return f"{self.batch.kode_batch} - {self.get_jenis_display()} ({self.tanggal})"
    
    def save(self, *args, **kwargs):
        is_new = self._state.adding  # True kalau ini pertama kali disimpan
        super().save(*args, **kwargs)

        if is_new:
            farm = self.farm
            # pakai nama owner kalau ada, kalau nggak fallback ke nama farm
            if getattr(farm, "owner", None):
                pelaku = farm.owner.get_full_name() or farm.owner.username
            else:
                pelaku = farm.name

            # PENEBARAN (kalau tanggal_tebar ada)
            if self.tanggal_tebar:
                Activity.objects.create(
                    batch=self,
                    tanggal=self.tanggal_tebar,
                    jenis="PENEBARAN",
                    lokasi=farm.location,
                    pelaku=pelaku,
                    keterangan="Penebaran benur awal siklus",
                )

            # PANEN
            Activity.objects.create(
                batch=self,
                tanggal=self.tanggal_panen,
                jenis="PANEN",
                lokasi=farm.location,
                pelaku=pelaku,
                keterangan="Panen utama",
            )

            # DARI_TAMBAK
            Activity.objects.create(
                batch=self,
                tanggal=timezone.localdate(),
                jenis="DARI_TAMBAK",
                lokasi=farm.location,
                pelaku=pelaku,
                keterangan="Batch didaftarkan ke sistem oleh farm owner",
            )