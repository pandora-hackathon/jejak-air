from django.contrib import messages
from django.shortcuts import redirect, render


# core/views.py (atau di app yang menangani dashboard)

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from batches.models import HarvestBatch # Asumsi model Batch ada di app 'batches'
from labs.models import LabTest # Asumsi model LabTest ada di app 'labs'
from profiles.models import UserProfile # Asumsi model UserProfile ada di app 'profiles'
from django.core.exceptions import ObjectDoesNotExist

def home(request):
    return render(request, "landing-page.html")

def is_lab_assistant(user):
    # Pastikan user sudah login dan memiliki role 'labAssistant'
    return user.is_authenticated and hasattr(user, 'userprofile') and user.userprofile.role == 'labAssistant'

@login_required
def dashboard_qc(request):
    if not is_lab_assistant(request.user):
        # Handle jika role bukan QC, misalnya redirect ke dashboard yang sesuai atau ke home
        return redirect('home') 

    user_profile = request.user.userprofile
    
    # 1. Batch yang Belum Diuji Lab (Membutuhkan Aksi)
    # Filter Batch yang is_deleted=False DAN lab_test__isnull=True
    batches_pending_test = HarvestBatch.objects.filter(
        is_deleted=False
    ).exclude(
        lab_test__isnull=False # Exclude batch yang sudah memiliki LabTest
    ).order_by('tanggal_panen')
    
    # 2. Histori Batch yang Pernah Diuji (Oleh QC yang sedang login)
    histori_lab_test = LabTest.objects.filter(
        qc=user_profile
    ).select_related('batch', 'lab').order_by('-tanggal_uji') # Optimasi query
    
    context = {
        'batches_pending_test': batches_pending_test,
        'histori_lab_test': histori_lab_test,
        'user_profile': user_profile,
    }
    return render(request, 'dashboard_qc.html', context)

@login_required
def dashboard_switcher(request):
    user = request.user
    
    try:
        # Cek apakah objek UserProfile ada. 
        # Jika relasi di model UserProfile diberi nama 'profile', maka aksesnya adalah user.profile
        # Jika tidak, aksesnya adalah user.userprofile (DEFAULT)
        user_profile = user.userprofile 
        
    except (AttributeError, ObjectDoesNotExist):
        # Tangani kasus jika userprofile tidak ada
        messages.error(request, "Profil pengguna tidak ditemukan. Silakan hubungi admin.")
        # Lakukan redirect ke home (atau view login/profile setup)
        return redirect('home') 

    role = user_profile.role # Akses role setelah yakin user_profile ada
    
    if role == 'labAssistant':
        return redirect('main:dashboard_qc')
    elif role == 'farmOwner':
        return redirect('main:dashboard_owner')
    elif role == 'admin':
        return redirect('main:dashboard_admin')
    else:
        messages.warning(request, "Role pengguna tidak dikenal.")
        return redirect('home')
    
def landing_page(request):
    kode_batch = (request.GET.get("kode_batch") or "").strip()

    if kode_batch:
        # Coba cari batch, kalau ada langsung redirect
        if HarvestBatch.objects.filter(pk=kode_batch).exists():
            return redirect("batches:batch_detail", pk=kode_batch)
        else:
            messages.error(request, "Batch dengan kode tersebut tidak ditemukan.")

    return render(request, "landing-page.html")