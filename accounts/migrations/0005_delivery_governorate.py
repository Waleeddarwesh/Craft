# Generated by Django 5.0.3 on 2024-06-21 04:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0004_alter_supplier_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='delivery',
            name='governorate',
            field=models.CharField(default='default_governorate', max_length=100),
        ),
    ]
