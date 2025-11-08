import datetime
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from authentication.forms import RegistrationForm, LoginForm
from django.contrib.auth import authenticate, login, logout

def register_view(request):
    if request.user.is_authenticated:
        return redirect(reverse("main:home"))
    
    form = RegistrationForm()
    if request.method == "POST":
        form = RegistrationForm(request.POST)

        if (form.is_valid()):
            user = form.save()
            login(request, user)
            response = JsonResponse({
                "redirect_url" : reverse("main:home"), # TODO: reverse ke create profile
                "status" : "success",
            })
            response.set_cookie('last_login', str(datetime.datetime.now()))
            return response
        return JsonResponse({
            "redirect_url" : reverse("authentication:register"), # TODO
            "status" : "failed",
        })
    return render(request, "register.html", {"form" : form})

def login_view(request):
    if request.user.is_authenticated:
        return redirect(reverse("main:home"))
    
    form = LoginForm(request, data=request.POST or None)
    if request.method == "POST":
        if (form.is_valid()):
            user = form.get_user()
            login(request, user)
            response = JsonResponse({
                "redirect_url" : reverse("main:home"), 
                "status" : "success",
            })
            response.set_cookie('last_login', str(datetime.datetime.now()))
            return response
        return JsonResponse({
            "redirect_url" : reverse("authentication:login"),
            "status" : "failed",
        })
    return render(request, "login.html", {"form" : form})

def logout_view(request):
    logout(request)
    response = JsonResponse({
        "redirect_url" : reverse("authentication:login"), 
        "status" : "success",
    })
    response.delete_cookie('last_login')
    return response