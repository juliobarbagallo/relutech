from django.db import models
from accounts.models import CustomUser

class Asset(models.Model):
    LAPTOP = 'laptop'
    KEYBOARD = 'keyboard'
    MOUSE = 'mouse'
    HEADSET = 'headset'
    MONITOR = 'monitor'
    ASSET_TYPE_CHOICES = [
        (LAPTOP, 'Laptop'),
        (KEYBOARD, 'Keyboard'),
        (MOUSE, 'Mouse'),
        (HEADSET, 'Headset'),
        (MONITOR, 'Monitor'),
    ]

    id = models.AutoField(primary_key=True)
    brand = models.CharField(max_length=50)
    model = models.CharField(max_length=50)
    type = models.CharField(max_length=50, choices=ASSET_TYPE_CHOICES)
    developer = models.ForeignKey(CustomUser, on_delete=models.CASCADE)

