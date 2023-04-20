from django.urls import path
from .views import UserLoginAPIView, AssetsAPIView
from . import views

app_name = 'api'

urlpatterns = [
    path('v1/user/login/', UserLoginAPIView.as_view(), name='login'),
    path('v1/developers/', views.DevelopersAPIView.as_view(), name='api_developers'),
    path('v1/developers/<int:pk>/', views.DevelopersAPIView.as_view(), name='api_developer_detail'),

    path('v1/assets/', AssetsAPIView.as_view(), name='all_assets'),
    path('v1/assets/<int:pk>/', AssetsAPIView.as_view(), name='asset-assignments'),
    path('v1/assets/<int:developer_id>/<int:asset_id>/', AssetsAPIView.as_view(), name='asset-delete'),
]
