# Generated by Django 4.2 on 2023-04-20 13:29

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("assets", "0002_alter_asset_developer"),
    ]

    operations = [
        migrations.AlterField(
            model_name="asset",
            name="developer",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="assets",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
