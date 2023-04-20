from django.contrib.auth.views import LoginView
from .models import CustomUser
from accounts.forms import CustomUserCreationForm
from django.shortcuts import redirect, render
from django.contrib.auth import authenticate, login, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import ensure_csrf_cookie
from django.utils.decorators import method_decorator
import json
from accounts.serializers import DeveloperSerializer



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

    @method_decorator(ensure_csrf_cookie)
    def dispatch(self, request, *args, **kwargs):
        if 'application/json' in request.content_type:
            return self.json_post(request)

        return super().dispatch(request, *args, **kwargs)

    def json_post(self, request):
        try:
            data = json.loads(request.body)
            username = data.get('username')
            password = data.get('password')
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON body'}, status=400)

        user = authenticate(username=username, password=password)
        if user is None:
            return JsonResponse({'error': 'Invalid username or password'}, status=400)

        login(request, user)

        return JsonResponse({'success': True})


@login_required
def dashboard(request):
    user = request.user
    
    if user.is_superuser:
        developers = CustomUser.objects.get_developers()
        print(f"{developers=}")
        context = {
            "user": user,
            "developers": developers,
        }
    else:
        context = {
            "user": user,
        }
    
    if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
        # developers_json = serialize('json', developers)
        developers_json = DeveloperSerializer(developers, many=True).data
        return JsonResponse({'developers': developers_json})
    else:
        return render(request, "dashboard.html", context)

User = get_user_model()

@login_required
def create_developer(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_admin = False
            user.save()
            messages.success(request, 'Developer user created successfully.')
            return redirect('dashboard')
    else:
        form = CustomUserCreationForm()
    return render(request, 'create_developer.html', {'form': form})