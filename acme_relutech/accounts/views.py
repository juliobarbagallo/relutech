from rest_framework import generics
from django.contrib.auth.views import LoginView
from .models import CustomUser
from accounts.forms import CustomUserCreationForm
from django.shortcuts import redirect, render
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required


def register(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password1")
            user = authenticate(username=username, password=password)
            login(request, user)
            return redirect("dashboard")
    else:
        form = CustomUserCreationForm()
    return render(request, "registration/register.html", {"form": form})


class CustomLoginView(LoginView):
    template_name = "registration/login.html"


@login_required
def dashboard(request):
    user = request.user
    
    
    context = {
        "user": user,
        
    }
    return render(request, "dashboard.html", context)