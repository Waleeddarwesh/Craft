# Generated by Django 5.0.3 on 2024-06-27 19:24

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0029_deliveryorder_returnrequest_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='deliveryorder',
            name='ReturnRequest',
        ),
    ]
