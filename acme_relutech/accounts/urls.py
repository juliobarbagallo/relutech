from django.contrib.auth.views import LogoutView
from django.urls import path

from .views import CustomLoginView, register, dashboard

urlpatterns = [
    path("register/", register, name="register"),
    path("login/", CustomLoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("dashboard/", dashboard, name="dashboard"),
]