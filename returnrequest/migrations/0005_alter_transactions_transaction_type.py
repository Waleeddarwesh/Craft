# Generated by Django 5.0.3 on 2024-06-27 22:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('returnrequest', '0004_deliveryreturnrequest'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transactions',
            name='transaction_type',
            field=models.CharField(choices=[('Withdraw', 'Withdraw'), ('Cash Back', 'Cash Back'), ('Returned Product', 'Returned Product'), ('Purshased Products', 'Purchased Products'), ('Refund Failed', 'Refund Failed')], max_length=50),
        ),
    ]
