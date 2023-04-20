from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate, login

from rest_framework.generics import ListCreateAPIView
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from accounts.models import CustomUser
from accounts.forms import CustomUserCreationForm
from .serializers import DeveloperSerializer, AssetSerializer, DeveloperWithAssetsSerializer

from assets.models import Asset


# TODO: Rename classes to friendly ones. install flake8, black and isort
class UserLoginAPIView(APIView):
    def post(self, request, format=None):
        username = request.data.get('username')
        password = request.data.get('password')

        user = authenticate(request, username=username, password=password)
        if user is None:
            return Response({'error': 'Invalid username or password'}, status=status.HTTP_400_BAD_REQUEST)

        login(request, user)
        return Response({'success': True})
    

class DevelopersAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not request.user.is_authenticated:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        
        if not request.user.is_admin:
            return Response(status=status.HTTP_403_FORBIDDEN)
        
        developers = CustomUser.objects.filter(is_admin=False).prefetch_related('assets')
        serializer = DeveloperWithAssetsSerializer(developers, many=True)

        return Response(serializer.data)

    def post(self, request):
        if not request.user.is_authenticated or not request.user.is_admin:
            return Response({'error': 'Not authorized'}, status=status.HTTP_401_UNAUTHORIZED)

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

        
    def put(self, request, pk):
        if not request.user.is_authenticated or not request.user.is_admin:
            return Response({'error': 'Not authorized'}, status=status.HTTP_401_UNAUTHORIZED)

        developer = CustomUser.objects.filter(pk=pk, is_admin=False).first()
        if developer is None:
            return Response({'error': 'Developer not found'}, status=status.HTTP_404_NOT_FOUND)

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
            return Response({'error': 'Not authorized'}, status=status.HTTP_401_UNAUTHORIZED)

        assets = Asset.objects.filter(developer=pk) if pk else Asset.objects.all()
        serializer = AssetSerializer(assets, many=True)
        return Response(serializer.data)

    def post(self, request, pk):
        if not request.user.is_authenticated or not request.user.is_admin:
            return Response({'error': 'Not authorized'}, status=status.HTTP_401_UNAUTHORIZED)

        developer = CustomUser.objects.filter(pk=pk, is_admin=False).first()
        if developer is None:
            return Response({'error': 'Developer not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = AssetSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        serializer.save(developer=developer)
        assets = Asset.objects.filter(developer=developer)
        serializer = AssetSerializer(assets, many=True)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, developer_id, asset_id):
        if not request.user.is_authenticated or not request.user.is_admin:
            return Response({'error': 'Not authorized'}, status=status.HTTP_401_UNAUTHORIZED)

        developer = CustomUser.objects.filter(pk=developer_id, is_admin=False).first()
        if developer is None:
            return Response({'error': 'Developer not found'}, status=status.HTTP_404_NOT_FOUND)

        asset = Asset.objects.filter(pk=asset_id, developer=developer).first()
        if asset is None:
            return Response({'error': 'Asset not found'}, status=status.HTTP_404_NOT_FOUND)

        asset.delete()
        assets = Asset.objects.filter(developer=developer)
        serializer = AssetSerializer(assets, many=True)
        return Response(serializer.data)
