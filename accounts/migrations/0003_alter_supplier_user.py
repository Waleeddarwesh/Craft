# Generated by Django 5.0.3 on 2024-05-19 00:50

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_remove_customer_buildingno_remove_customer_city_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='supplier',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='Supplier', to=settings.AUTH_USER_MODEL),
        ),
    ]
