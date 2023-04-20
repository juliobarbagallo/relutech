from accounts.forms import CustomUserCreationForm
from accounts.models import CustomUser
from accounts.serializers import DeveloperSerializer, SwaggDeveloperSerializer
from assets.models import Asset

# from .serializers import AssetSerializer, DeveloperWithAssetsSerializer
from assets.serializers import AssetSerializer, DeveloperWithAssetsSerializer
from django.contrib.auth import authenticate, login
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from licenses.models import License
from licenses.serializers import DeveloperWithLicensesSerializer, LicenseSerializer
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView


# TODO: Rename classes to friendly ones. install flake8, black and isort
class UserLoginAPIView(APIView):
    def post(self, request, format=None):
        username = request.data.get("username")
        password = request.data.get("password")

        user = authenticate(request, username=username, password=password)
        if user is None:
            return Response(
                {"error": "Invalid username or password"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        login(request, user)
        return Response({"success": True})


class DevelopersAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Get developers, their assets and licenses",
        responses={
            200: openapi.Response(
                description="OK",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "assets": openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=DeveloperWithAssetsSerializer().data,
                        ),
                        "licenses": openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=DeveloperWithLicensesSerializer().data,
                        ),
                    },
                ),
            ),
            401: "Unauthorized",
            403: "Forbidden",
        },
    )
    def get(self, request):
        if not request.user.is_authenticated:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        if not request.user.is_admin:
            return Response(status=status.HTTP_403_FORBIDDEN)

        developers_asset = CustomUser.objects.filter(is_admin=False).prefetch_related(
            "assets"
        )
        developers_licenses = CustomUser.objects.filter(
            is_admin=False
        ).prefetch_related("licenses")
        asset_serializer = DeveloperWithAssetsSerializer(developers_asset, many=True)
        license_serializer = DeveloperWithLicensesSerializer(
            developers_licenses, many=True
        )
        data = {"assets": asset_serializer.data, "licenses": license_serializer.data}

        return Response(data)

    @swagger_auto_schema(
        request_body=SwaggDeveloperSerializer,
        responses={200: "OK"},
        operation_summary="Allows user developers creation",
        operation_description="It creates new developers user on the DataBase.",
    )
    def post(self, request):
        if not request.user.is_authenticated or not request.user.is_admin:
            return Response(
                {"error": "Not authorized"}, status=status.HTTP_401_UNAUTHORIZED
            )

        form = CustomUserCreationForm(request.data)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_admin = False
            user.save()
            developers = CustomUser.objects.filter(is_admin=False)
            serializer = DeveloperSerializer(developers, many=True)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        # else:
        return Response(form.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "username": openapi.Schema(type=openapi.TYPE_STRING),
                "email": openapi.Schema(type=openapi.TYPE_STRING),
                "is_active": openapi.Schema(type=openapi.TYPE_BOOLEAN),
                "is_admin": openapi.Schema(type=openapi.TYPE_BOOLEAN),
            },
            manual_parameters=[
                openapi.Parameter(
                    "pk",
                    openapi.IN_PATH,
                    type=openapi.TYPE_INTEGER,
                    description="The ID of the developer to update",
                    required=True,
                ),
            ],
            required=["username"],
        ),
        responses={
            200: openapi.Response(description="Updated developer successfully"),
            400: openapi.Response(description="Invalid request data"),
            401: openapi.Response(description="Not authorized"),
            404: openapi.Response(description="Developer not found"),
        },
        operation_summary="Updates a developer",
        operation_description="Updates a developer identified by the given primary key",
    )
    def put(self, request, pk):
        if not request.user.is_authenticated or not request.user.is_admin:
            return Response(
                {"error": "Not authorized"}, status=status.HTTP_401_UNAUTHORIZED
            )

        developer = CustomUser.objects.filter(pk=pk, is_admin=False).first()
        if developer is None:
            return Response(
                {"error": "Developer not found"}, status=status.HTTP_404_NOT_FOUND
            )

        serializer = DeveloperSerializer(developer, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            developers = CustomUser.objects.filter(is_admin=False)
            serializer = DeveloperSerializer(developers, many=True)
            return Response(serializer.data)
        # else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AssetsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk=None):
        if not request.user.is_authenticated or not request.user.is_admin:
            return Response(
                {"error": "Not authorized"}, status=status.HTTP_401_UNAUTHORIZED
            )

        assets = Asset.objects.filter(developer=pk) if pk else Asset.objects.all()
        serializer = AssetSerializer(assets, many=True)
        return Response(serializer.data)

    def post(self, request, pk):
        if not request.user.is_authenticated or not request.user.is_admin:
            return Response(
                {"error": "Not authorized"}, status=status.HTTP_401_UNAUTHORIZED
            )

        developer = CustomUser.objects.filter(pk=pk, is_admin=False).first()
        if developer is None:
            return Response(
                {"error": "Developer not found"}, status=status.HTTP_404_NOT_FOUND
            )

        serializer = AssetSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        serializer.save(developer=developer)
        assets = Asset.objects.filter(developer=developer)
        serializer = AssetSerializer(assets, many=True)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, developer_id, asset_id):
        if not request.user.is_authenticated or not request.user.is_admin:
            return Response(
                {"error": "Not authorized"}, status=status.HTTP_401_UNAUTHORIZED
            )

        developer = CustomUser.objects.filter(pk=developer_id, is_admin=False).first()
        if developer is None:
            return Response(
                {"error": "Developer not found"}, status=status.HTTP_404_NOT_FOUND
            )

        asset = Asset.objects.filter(pk=asset_id, developer=developer).first()
        if asset is None:
            return Response(
                {"error": "Asset not found"}, status=status.HTTP_404_NOT_FOUND
            )

        asset.delete()
        assets = Asset.objects.filter(developer=developer)
        serializer = AssetSerializer(assets, many=True)
        return Response(serializer.data)


class LicensesAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk=None):
        if not request.user.is_authenticated or not request.user.is_admin:
            return Response(
                {"error": "Not authorized"}, status=status.HTTP_401_UNAUTHORIZED
            )

        licenses = License.objects.filter(developer=pk) if pk else License.objects.all()
        serializer = LicenseSerializer(licenses, many=True)
        return Response(serializer.data)

    def post(self, request, pk):
        if not request.user.is_authenticated or not request.user.is_admin:
            return Response(
                {"error": "Not authorized"}, status=status.HTTP_401_UNAUTHORIZED
            )

        developer = CustomUser.objects.filter(pk=pk, is_admin=False).first()
        if developer is None:
            return Response(
                {"error": "Developer not found"}, status=status.HTTP_404_NOT_FOUND
            )

        serializer = LicenseSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        serializer.save(developer=developer)
        licenses = License.objects.filter(developer=developer)
        serializer = LicenseSerializer(licenses, many=True)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, developer_id, license_id):
        if not request.user.is_authenticated or not request.user.is_admin:
            return Response(
                {"error": "Not authorized"}, status=status.HTTP_401_UNAUTHORIZED
            )

        developer = CustomUser.objects.filter(pk=developer_id, is_admin=False).first()
        if developer is None:
            return Response(
                {"error": "Developer not found"}, status=status.HTTP_404_NOT_FOUND
            )

        license = License.objects.filter(pk=license_id, developer=developer).first()
        if license is None:
            return Response(
                {"error": "License not found"}, status=status.HTTP_404_NOT_FOUND
            )

        license.delete()
        licenses = License.objects.filter(developer=developer)
        serializer = LicenseSerializer(licenses, many=True)
        return Response(serializer.data)
