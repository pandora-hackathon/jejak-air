from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.urls import reverse
from farms.forms import FarmForm, CityForm
from farms.models import Farm
from profiles.models import UserProfile

@login_required(login_url='/authentication/login')
def create_farm(request):
    farm_form = FarmForm(request.POST or None)
    city_form = CityForm(request.POST or None)

    if request.method == 'POST':
        if farm_form.is_valid() and city_form.is_valid():
            city_obj = city_form.save() 
            farm_entry = farm_form.save(commit=False)
            farm_entry.city = city_obj
            farm_entry.owner = UserProfile.objects.get(user=request.user)
            farm_entry.save()
            return redirect('main:home')

    context = {
        'farm_form': farm_form,
        'city_form': city_form,
    }

    return render(request, "create_farm.html", context)

@login_required(login_url='/authentication/login')
def edit_farm(request, id):
    farm = get_object_or_404(Farm, pk=id)
    form = FarmForm(request.POST or None, instance=farm)
    if form.is_valid() and request.method == 'POST':
        form.save()
        return redirect('main:home')

    context = {
        'form': form
    }

    return render(request, "edit_farm.html", context)

@login_required(login_url='/authentication/login')
def delete_farm(request, id):
    farm = get_object_or_404(Farm, pk=id)
    farm.delete()
    return HttpResponseRedirect(reverse('main:home'))