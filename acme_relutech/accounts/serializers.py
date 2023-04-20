from accounts.models import CustomUser
from rest_framework import serializers


class DeveloperSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ["last_login", "email", "username", "is_active"]


class SwaggDeveloperSerializer(serializers.ModelSerializer):
    email = serializers.EmailField()
    password1 = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)
    is_admin = serializers.BooleanField(default=False)

    class Meta:
        model = CustomUser
        fields = ["email", "username", "password1", "password2", "is_admin"]

    def validate(self, data):
        if data["password1"] != data["password2"]:
            raise serializers.ValidationError("The passwords do not match.")
        return data
