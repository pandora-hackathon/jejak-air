# batches/views.py
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .models import HarvestBatch, Activity
from .forms import HarvestBatchForm  # tambahin ActivityManualForm nanti


def _require_farm_owner(request):
    user = request.user
    if not user.is_authenticated:
        raise PermissionDenied("Silakan login terlebih dahulu.")

    if getattr(user, "role", None) != "farmOwner":
        raise PermissionDenied("Hanya pemilik tambak yang boleh mengelola batch.")

    profile = getattr(user, "profile", None)
    if profile is None:
        raise PermissionDenied("Profil pengguna belum lengkap. Silakan lengkapi data diri.")

    return profile


def _check_batch_owner(request, batch: HarvestBatch):
    profile = _require_farm_owner(request)
    if batch.farm.owner_id != profile.id:
        raise PermissionDenied("Anda tidak berhak mengubah batch dari tambak lain.")
    return profile


# @login_required
def batch_list(request):
    profile = _require_farm_owner(request)

    batches = (
        HarvestBatch.objects
        .select_related("farm", "commodity")
        .filter(farm__owner=profile)
    )

    return render(request, "batch_list.html", {"batches": batches})


# @login_required
def batch_detail(request, pk):
    """
    Detail 1 batch + daftar activity (timeline)
    pk di sini adalah kode_batch (CharField primary_key=True).
    """
    batch = get_object_or_404(
        HarvestBatch.objects
        .select_related("farm", "commodity")
        .prefetch_related("activities"),
        pk=pk,
    )
    # _check_batch_owner(request, batch)

    activities = batch.activities.all()
    has_received_activity = activities.filter(jenis="DITERIMA").exists()

    context = {
        "batch": batch,
        "activities": activities,
        "has_received_activity": has_received_activity,
    }
    return render(request, "batch_detail.html", context)


# @login_required
def batch_create(request):
    _require_farm_owner(request)

    if request.method == "POST":
        form = HarvestBatchForm(request.POST, user=request.user)
        if form.is_valid():
            batch = form.save()
            return redirect("batches:batch_detail", pk=batch.pk)
    else:
        form = HarvestBatchForm(user=request.user)

    return render(request, "batch_form.html", {"form": form, "mode": "create"})


# @login_required
def batch_update(request, pk):
    batch = get_object_or_404(HarvestBatch, pk=pk)
    _check_batch_owner(request, batch)

    if request.method == "POST":
        form = HarvestBatchForm(request.POST, instance=batch, user=request.user)
        if form.is_valid():
            batch = form.save()
            return redirect("batches:batch_detail", pk=batch.pk)
    else:
        form = HarvestBatchForm(instance=batch, user=request.user)

    context = {"form": form, "mode": "update", "batch": batch}
    return render(request, "batch_form.html", context)


# @login_required
def batch_delete(request, pk):
    batch = get_object_or_404(HarvestBatch, pk=pk)
    _check_batch_owner(request, batch)

    if request.method == "POST":
        batch.delete()
        return redirect("batches:batch_list")

    return render(request, "batch_confirm_delete.html", {"batch": batch})

def _get_pelaku_from_farm(farm):
    pelaku = farm.name
    owner_profile = getattr(farm, "owner", None)
    if owner_profile is not None:
        user = getattr(owner_profile, "user", None)
        if user is not None:
            pelaku = user.get_full_name() or user.username
    return pelaku


# @login_required
def batch_mark_shipped(request, pk):
    """
    Dipanggil saat tombol 'Kirim' diklik.
    Hanya boleh kalau shipment_status == 'LAYAK_KIRIM'.
    Akan set is_shipped=True dan tambahkan activity DIEKSPOR.
    """
    batch = get_object_or_404(HarvestBatch, pk=pk)
    _check_batch_owner(request, batch)

    if request.method == "POST" and batch.shipment_status == "LAYAK_KIRIM":
        batch.is_shipped = True
        batch.save()

        farm = batch.farm
        pelaku = _get_pelaku_from_farm(farm)

        Activity.objects.create(
            batch=batch,
            tanggal=timezone.now().date(),
            jenis="DIEKSPOR",
            lokasi=farm.location,
            pelaku=pelaku,
            keterangan="Batch dikirim untuk ekspor.",
        )

    return redirect("batches:batch_detail", pk=batch.pk)


# @login_required
def batch_mark_received(request, pk):
    """
    Dipanggil saat tombol 'Diterima' diklik.
    Menambahkan activity DITERIMA satu kali saja.
    """
    batch = get_object_or_404(HarvestBatch, pk=pk)
    _check_batch_owner(request, batch)

    if request.method == "POST":
        already = batch.activities.filter(jenis="DITERIMA").exists()
        if not already:
            farm = batch.farm
            pelaku = _get_pelaku_from_farm(farm)

            Activity.objects.create(
                batch=batch,
                tanggal=timezone.now().date(),
                jenis="DITERIMA",
                lokasi=batch.tujuan,
                pelaku=pelaku,
                keterangan="Batch diterima oleh pihak tujuan.",
            )

    return redirect("batches:batch_detail", pk=batch.pk)


from .forms import ActivityManualForm 


# @login_required
def activity_manual_create(request, pk):
    """
    Tambah activity dengan jenis LAINNYA untuk batch tertentu.
    """
    batch = get_object_or_404(HarvestBatch, pk=pk)
    _check_batch_owner(request, batch)

    if request.method == "POST":
        form = ActivityManualForm(request.POST)
        if form.is_valid():
            activity = form.save(commit=False)
            activity.batch = batch
            activity.jenis = "LAINNYA"
            activity.save()
            return redirect("batches:batch_detail", pk=batch.pk)
    else:
        form = ActivityManualForm()

    context = {"batch": batch, "form": form}
    return render(request, "batches/activity_manual_form.html", context)
