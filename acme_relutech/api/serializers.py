from rest_framework  import serializers
from accounts.models import CustomUser

class DeveloperSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['last_login', 'email', 'username', 'is_active']