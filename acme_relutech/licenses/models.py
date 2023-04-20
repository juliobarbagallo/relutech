from django.db import models
from accounts.models import CustomUser

class License(models.Model):
    id = models.AutoField(primary_key=True)
    software = models.CharField(max_length=50)
    developer = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='licenses')
