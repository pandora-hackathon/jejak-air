from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import UserProfile
from .forms import OwnerProfileForm


@login_required
def create_profile(request):
    user = request.user
    profile = user.profile  # dibuat otomatis oleh signal

    # Jika role labAssistant → langsung ke dashboard
    if user.role == "labAssistant":
        user.has_profile = True
        user.save()
        return redirect("labAssistant-dashboard")

    # Jika role admin → tidak mengisi profile
    if user.role == "admin":
        return redirect("admin-dashboard")

    # Jika role farmOwner dan profile SUDAH lengkap
    if user.has_profile and user.role == "farmOwner":
        return redirect("farmOwner-dashboard")

    # === FARM OWNER FORM ===
    if request.method == "POST":
        form = OwnerProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            user.has_profile = True
            user.save()
            return redirect("farmOwner-dashboard")
    else:
        form = OwnerProfileForm(instance=profile)

    return render(request, "create-profile.html", {"form": form})
