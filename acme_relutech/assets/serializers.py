from accounts.models import CustomUser
from assets.models import Asset
from rest_framework import serializers


class AssetSerializer(serializers.ModelSerializer):
    developer = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Asset
        fields = ["id", "brand", "model", "type", "developer"]
        read_only_fields = ("developer",)


class DeveloperWithAssetsSerializer(serializers.ModelSerializer):
    assets = AssetSerializer(many=True, read_only=True)

    class Meta:
        model = CustomUser
        fields = ["id", "username", "email", "assets"]
