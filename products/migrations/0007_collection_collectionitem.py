# Generated by Django 5.0.3 on 2024-05-18 21:53

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_remove_customer_buildingno_remove_customer_city_and_more'),
        ('products', '0006_alter_product_stock'),
    ]

    operations = [
        migrations.CreateModel(
            name='Collection',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('supplier', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='collections', to='accounts.supplier')),
            ],
        ),
        migrations.CreateModel(
            name='CollectionItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('collection', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='products.collection')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='collection_items', to='products.product')),
            ],
        ),
    ]
