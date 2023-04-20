from django.urls import path
from .views import UserLoginAPIView
from . import views

app_name = 'api'

urlpatterns = [
    path('v1/user/login/', UserLoginAPIView.as_view(), name='login'),
    path('v1/developers/', views.DeveloperListCreateAPIView.as_view(), name='api_developers'),
    path('v1/developers/<int:pk>/', views.DeveloperListCreateAPIView.as_view(), name='api_developer_detail'),
]
