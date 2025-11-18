from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render

from .models import HarvestBatch
from .forms import HarvestBatchForm


def _require_farm_owner(request):
    """
    Pastikan user adalah farmOwner dan punya UserProfile.
    Return: UserProfile owner.
    """
    user = request.user
    if not user.is_authenticated:
        raise PermissionDenied("Silakan login terlebih dahulu.")

    # role diambil dari custom User (authentication.User)
    if getattr(user, "role", None) != "farmOwner":
        raise PermissionDenied("Hanya pemilik tambak yang boleh mengelola batch.")

    # pastikan punya profil
    profile = getattr(user, "profile", None)
    if profile is None:
        raise PermissionDenied("Profil pengguna belum lengkap. Silakan lengkapi data diri.")

    return profile


def _check_batch_owner(request, batch: HarvestBatch):
    """
    Raise PermissionDenied kalau user sekarang bukan owner farm dari batch ini.
    """
    profile = _require_farm_owner(request)
    if batch.farm.owner_id != profile.id:
        raise PermissionDenied("Anda tidak berhak mengubah batch dari tambak lain.")
    return profile


@login_required
def batch_list(request):
    """
    List batch HANYA untuk farm yang dimiliki user (farmOwner).
    """
    profile = _require_farm_owner(request)

    batches = (
        HarvestBatch.objects
        .select_related("farm", "commodity")
        .filter(farm__owner=profile)
    )

    context = {
        "batches": batches,
    }
    return render(request, "batches/batch_list.html", context)


@login_required
def batch_detail(request, pk):
    """
    Detail 1 batch, hanya bisa diakses owner farm-nya.
    """
    batch = get_object_or_404(HarvestBatch, pk=pk)
    _check_batch_owner(request, batch)

    context = {
        "batch": batch,
    }
    return render(request, "batches/batch_detail.html", context)


@login_required
def batch_create(request):
    """
    Buat batch baru.
    - Hanya farmOwner.
    - Pilihan farm di form otomatis terfilter ke farm milik user.
    - kode_batch + Activity PENEBARAN / PANEN / DARI_TAMBAK
      dibuat otomatis di model.save().
    """
    _require_farm_owner(request)

    if request.method == "POST":
        form = HarvestBatchForm(request.POST, user=request.user)
        if form.is_valid():
            batch = form.save()  # ini akan memicu save() di model
            return redirect("batches:batch_detail", pk=batch.pk)
    else:
        form = HarvestBatchForm(user=request.user)

    context = {
        "form": form,
        "mode": "create",
    }
    return render(request, "batches/batch_form.html", context)


@login_required
def batch_update(request, pk):
    """
    Edit batch.
    - Hanya boleh oleh owner farm batch tersebut.
    """
    batch = get_object_or_404(HarvestBatch, pk=pk)
    _check_batch_owner(request, batch)

    if request.method == "POST":
        form = HarvestBatchForm(request.POST, instance=batch, user=request.user)
        if form.is_valid():
            batch = form.save()
            return redirect("batches:batch_detail", pk=batch.pk)
    else:
        form = HarvestBatchForm(instance=batch, user=request.user)

    context = {
        "form": form,
        "mode": "update",
        "batch": batch,
    }
    return render(request, "batches/batch_form.html", context)


@login_required
def batch_delete(request, pk):
    """
    Hapus batch.
    - Hanya boleh oleh owner farm batch tersebut.
    - Activity otomatis ikut kehapus (on_delete=CASCADE).
    """
    batch = get_object_or_404(HarvestBatch, pk=pk)
    _check_batch_owner(request, batch)

    if request.method == "POST":
        batch.delete()
        return redirect("batches:batch_list")

    context = {
        "batch": batch,
    }
    return render(request, "batches/batch_confirm_delete.html", context)
