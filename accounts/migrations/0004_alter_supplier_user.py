# Generated by Django 5.0.3 on 2024-05-19 01:58

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_alter_supplier_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='supplier',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
