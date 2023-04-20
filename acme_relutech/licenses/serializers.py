from rest_framework import serializers
from licenses.models import License
from accounts.models import CustomUser

class LicenseSerializer(serializers.ModelSerializer):
    developer = serializers.PrimaryKeyRelatedField(read_only=True)
    class Meta:
        model = License
        fields = ['id', 'software', 'developer']
        read_only_fields = ('developer',)

class DeveloperWithLicensesSerializer(serializers.ModelSerializer):
    assets = LicenseSerializer(many=True, read_only=True)

    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'licenses']
