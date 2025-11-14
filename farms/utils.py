from datetime import timedelta

from django.utils import timezone

from .models import Farm


def recalculate_farm_risk(farm: Farm) -> int:
    """
    Hitung Farm Risk Score berdasarkan % batch MASALAH
    dalam 6 bulan terakhir (pakai tanggal_panen).
    """

    today = timezone.now().date()
    six_months_ago = today - timedelta(days=180)  # approx 6 bulan

    qs = farm.batches.filter(tanggal_panen__gte=six_months_ago)
    total_batch = qs.count()

    if total_batch == 0:
        score = 30
    else:
        jumlah_masalah = qs.filter(quality_status="MASALAH").count()
        ratio = jumlah_masalah / total_batch

        if ratio <= 0.10:
            score = 30
        elif ratio <= 0.30:
            score = 60
        else:
            score = 85

    farm.risk_score = score
    farm.save(update_fields=["risk_score"])
    return score
