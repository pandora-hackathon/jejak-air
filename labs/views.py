from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import ObjectDoesNotExist
from .models import Laboratory, LabTest
from .forms import LaboratoryForm, LabTestForm
from batches.models import HarvestBatch

def is_admin(user):
    return user.is_authenticated and hasattr(user, 'userprofile') and user.userprofile.role == 'admin'

def is_lab_assistant(user):
    return user.is_authenticated and hasattr(user, 'userprofile') and user.userprofile.role == 'labAssistant'

@login_required
@user_passes_test(is_admin)
def laboratory_list(request):
    laboratories = Laboratory.objects.all()
    context = {'laboratories': laboratories}
    return render(request, 'labs/laboratory_list.html', context)

@login_required
@user_passes_test(is_admin)
def laboratory_create(request):
    if request.method == 'POST':
        form = LaboratoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Laboratorium berhasil ditambahkan.")
            return redirect('labs:laboratory_list')
    else:
        form = LaboratoryForm()
    return render(request, 'labs/laboratory_form.html', {'form': form, 'title': 'Tambah Laboratorium'})

@login_required
@user_passes_test(is_admin)
def laboratory_detail(request, pk):
    lab = get_object_or_404(Laboratory, pk=pk)
    return render(request, 'labs/laboratory_detail.html', {'lab': lab})

@login_required
@user_passes_test(is_admin)
def laboratory_delete(request, pk):
    lab = get_object_or_404(Laboratory, pk=pk)
    if request.method == 'POST':
        lab.delete()
        messages.success(request, f"Laboratorium {lab.nama} berhasil dihapus.")
        return redirect('labs:laboratory_list')
    return render(request, 'labs/laboratory_confirm_delete.html', {'lab': lab})

@login_required
@user_passes_test(is_lab_assistant)
def labtest_create(request, kode_batch):
    batch = get_object_or_404(HarvestBatch, kode_batch=kode_batch)

    if hasattr(batch, 'lab_test'):
        messages.warning(request, f"Batch {kode_batch} sudah memiliki hasil uji lab.")
        return redirect('batches:detail', kode_batch=kode_batch)

    if request.method == 'POST':
        form = LabTestForm(request.POST, initial={'qc': request.user.userprofile})
        
        if 'qc' in form.fields:
             form.instance.qc = request.user.userprofile
        
        if form.is_valid():
            lab_test = form.save(commit=False)
            lab_test.batch = batch
            
            if not lab_test.qc_id:
                lab_test.qc = request.user.userprofile
                
            lab_test.save()
            messages.success(request, f"Hasil uji lab untuk batch {kode_batch} berhasil ditambahkan. Risk score batch diperbarui.")
            return redirect('batches:detail', kode_batch=kode_batch)
    else:
        form = LabTestForm(initial={'qc': request.user.userprofile})

    context = {
        'form': form,
        'batch': batch,
        'title': f'Tambah Hasil Uji Lab untuk Batch {kode_batch}'
    }
    return render(request, 'labs/labtest_form.html', context)