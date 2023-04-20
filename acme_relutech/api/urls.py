from django.urls import path
from .views import UserLoginAPIView, AssetAssignmentsAPIView
from . import views

app_name = 'api'

urlpatterns = [
    path('v1/user/login/', UserLoginAPIView.as_view(), name='login'),
    path('v1/developers/', views.DeveloperListCreateAPIView.as_view(), name='api_developers'),
    path('v1/developers/<int:pk>/', views.DeveloperListCreateAPIView.as_view(), name='api_developer_detail'),

    path('v1/assets/', AssetAssignmentsAPIView.as_view(), name='all_assets'),
    path('v1/assets/<int:pk>/', AssetAssignmentsAPIView.as_view(), name='asset-assignments'),
    path('v1/assets/<int:developer_id>/<int:asset_id>/', AssetAssignmentsAPIView.as_view(), name='asset-assignments-detail'),
]
