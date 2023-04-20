from rest_framework  import serializers
from accounts.models import CustomUser
from assets.models import Asset

class DeveloperSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['last_login', 'email', 'username', 'is_active']

class AssetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Asset
        fields = ['id', 'brand', 'model', 'type', 'developer']

class DeveloperWithAssetsSerializer(serializers.ModelSerializer):
    assets = AssetSerializer(many=True, read_only=True)

    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'assets']