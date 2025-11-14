from .models import HarvestBatch
from farms.utils import recalculate_farm_risk


def recalculate_batch_risk(batch: HarvestBatch):
    """
    Hitung risk_score final untuk satu batch berdasarkan:

    - base_risk dari LabTest Cs-137
    - penalti extra dari Farm.risk_score
    """

    farm = batch.farm

    # pastikan farm risk up to date
    if farm.risk_score is None:
        farm_risk = recalculate_farm_risk(farm)
    else:
        farm_risk = farm.risk_score

    # cek LabTest (di desain ini 1:1)
    lab_test = getattr(batch, "lab_test", None)

    # Kasus 3 – belum ada LabTest
    if lab_test is None:
        batch.quality_status = "PENDING"
        batch.risk_score = None  # supaya shipment_status = BELUM_DITINJAU
        batch.save(update_fields=["quality_status", "risk_score"])
        return None

    # Kasus 1 – ada LabTest bermasalah
    if lab_test.kesimpulan == "BERMASALAH":
        base_risk = 90
        batch.quality_status = "MASALAH"

    else:
        # Kasus 2 – ada LabTest dan kesimpulan AMAN
        if lab_test.batas_aman_cs137:
            worst_ratio = lab_test.nilai_cs137 / lab_test.batas_aman_cs137
        else:
            worst_ratio = 1.0  # fallback: treat as dekat limit

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
