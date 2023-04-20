from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    is_admin = forms.BooleanField(required=False)

    class Meta:
        model = get_user_model()
        fields = ("username", "email", "password1", "password2", "is_admin")
