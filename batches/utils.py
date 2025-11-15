from __future__ import annotations

from typing import TYPE_CHECKING

from django.utils import timezone
from django.apps import apps

from farms.utils import recalculate_farm_risk

if TYPE_CHECKING:
    from .models import HarvestBatch

DEFAULT_BATAS_AMAN_CS137 = 500


def get_batas_aman_cs137(batch: HarvestBatch) -> float:
    """
    Ambil batas aman Cs-137 untuk sebuah batch.

    Prioritas:
    1. Kalau batch.commodity punya atribut default_batas_aman_cs137 dan tidak None,
       pakai itu.
    2. Kalau tidak ada / None → pakai DEFAULT_BATAS_AMAN_CS137 (500).
    """
    commodity = getattr(batch, "commodity", None)
    if commodity is not None:
        batas = getattr(commodity, "default_batas_aman_cs137", None)
        if batas is not None:
            return batas
    return DEFAULT_BATAS_AMAN_CS137


def recalculate_batch_risk(batch: HarvestBatch):
    """
    Hitung risk_score final untuk satu batch berdasarkan:

    - base_risk dari LabTest Cs-137
    - penalti extra dari Farm.risk_score
    """

    farm = batch.farm

    # Pastikan farm_risk up to date
    if farm.risk_score is None:
        farm_risk = recalculate_farm_risk(farm)
    else:
        farm_risk = farm.risk_score

    # Cek LabTest (desain: 1:1 per batch)
    lab_test = getattr(batch, "lab_test", None)

    # Kasus 3 – belum ada LabTest
    if lab_test is None:
        batch.quality_status = "PENDING"
        # risk_score dikosongkan supaya shipment_status = BELUM_DITINJAU
        batch.risk_score = None
        batch.save(update_fields=["quality_status", "risk_score"])
        return None

    # Kasus 1 – ada LabTest bermasalah
    if lab_test.kesimpulan == "BERMASALAH":
        base_risk = 90
        batch.quality_status = "MASALAH"

    else:
        # Kasus 2 – ada LabTest dan kesimpulan AMAN
        batas = get_batas_aman_cs137(batch)  # ← ambil dari komoditas + fallback global

        # batas dijamin > 0 karena fallback = 500,
        # tapi tetap kita jaga case aneh (misal di-set 0)
        if batas:
            worst_ratio = lab_test.nilai_cs137 / batas
        else:
            # fallback ekstrem: kalau batas tidak terdefinisi masuk case ini,
            # anggap dekat limit
            worst_ratio = 1.0

        if worst_ratio <= 0.50:
            base_risk = 30
        elif worst_ratio <= 0.80:
            base_risk = 50
        else:
            base_risk = 75

        batch.quality_status = "AMAN"

    # Penyesuaian dengan Farm Risk (likelihood)
    if farm_risk <= 40:
        extra = 0
    elif farm_risk <= 70:
        extra = 10
    else:
        extra = 20

    batch.risk_score = min(100, base_risk + extra)
    batch.save(update_fields=["quality_status", "risk_score"])
    return batch.risk_score


def generate_batch_code(farm, tanggal_panen=None) -> str:
    """
    Generate kode_batch unik berdasarkan:
    - kode kota (City.code)
    - ID farm
    - tanggal panen (YYYYMMDD)
    - nomor urut 3 digit
    Contoh: IDM-F0012-20250301-001
    """

    HarvestBatch = apps.get_model("batches", "HarvestBatch")

    city = getattr(farm, "city", None)
    city_code = getattr(city, "code", None) or "XXX"

    # farm id bisa None sebelum disimpan, jadi fallback kalau perlu
    if farm.id:
        farm_part = f"F{farm.id:04d}"
    else:
        farm_part = "F0000"

    if tanggal_panen:
        date_part = tanggal_panen.strftime("%Y%m%d")
    else:
        date_part = timezone.now().strftime("%Y%m%d")

    prefix = f"{city_code}-{farm_part}-{date_part}"

    # Cari kode terakhir dengan prefix ini, lalu increment suffix
    last_batch = (
        HarvestBatch.objects.filter(kode_batch__startswith=prefix)
        .order_by("-kode_batch")
        .first()
    )

    if last_batch and last_batch.kode_batch:
        # Format: PREFIX-XYZ  → ambil bagian akhir
        try:
            last_suffix_str = last_batch.kode_batch.split("-")[-1]
            last_suffix = int(last_suffix_str)
        except (ValueError, IndexError):
            last_suffix = 0
    else:
        last_suffix = 0

    new_suffix = last_suffix + 1
    return f"{prefix}-{new_suffix:03d}"
