# Generated by Django 5.0.3 on 2024-06-25 03:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0005_delivery_governorate'),
    ]

    operations = [
        migrations.AlterField(
            model_name='address',
            name='BuildingNO',
            field=models.CharField(max_length=10, null=True),
        ),
    ]