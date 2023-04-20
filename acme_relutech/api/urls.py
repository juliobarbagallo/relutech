from django.urls import path

from . import views
from .views import AssetsAPIView, LicensesAPIView, UserLoginAPIView

app_name = "api"

urlpatterns = [
    # users
    path("v1/user/login/", UserLoginAPIView.as_view(), name="login"),
    path("v1/developers/", views.DevelopersAPIView.as_view(), name="api_developers"),
    path(
        "v1/developers/<int:pk>/",
        views.DevelopersAPIView.as_view(),
        name="api_developer_detail",
    ),
    # Assets
    path("v1/assets/", AssetsAPIView.as_view(), name="all_assets"),
    path("v1/assets/<int:pk>/", AssetsAPIView.as_view(), name="asset-assignments"),
    path(
        "v1/assets/<int:developer_id>/<int:asset_id>/",
        AssetsAPIView.as_view(),
        name="asset-delete",
    ),
    # Licenses
    path("v1/licenses/", LicensesAPIView.as_view(), name="all_licenses"),
    path(
        "v1/licenses/<int:pk>/", LicensesAPIView.as_view(), name="license-assignments"
    ),
    path(
        "v1/licenses/<int:developer_id>/<int:license_id>/",
        LicensesAPIView.as_view(),
        name="license-delete",
    ),
]
