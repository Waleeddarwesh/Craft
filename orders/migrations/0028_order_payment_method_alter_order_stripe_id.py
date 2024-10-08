# Generated by Django 5.0.3 on 2024-06-27 02:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0027_order_supplier'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='payment_method',
            field=models.CharField(choices=[('Cash on Delivery ', 'Cash On Delivery'), ('Credit Card', 'Credit Card'), ('Balance', 'Balance')], default='Cash on Delivery ', max_length=50),
        ),
        migrations.AlterField(
            model_name='order',
            name='stripe_id',
            field=models.CharField(blank=True, max_length=250, null=True),
        ),
    ]
