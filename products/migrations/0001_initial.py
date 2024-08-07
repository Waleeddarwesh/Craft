# Generated by Django 5.0.3 on 2024-04-29 16:28

import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('CategoryID', models.AutoField(primary_key=True, serialize=False)),
                ('Title', models.CharField(max_length=100)),
                ('Description', models.TextField()),
                ('Picture', models.ImageField(blank=True, null=True, upload_to='category_images/%y/%m/%d')),
                ('Active', models.BooleanField(default=True)),
                ('Slug', models.SlugField(blank=True, null=True, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='MatCategory',
            fields=[
                ('MatID', models.AutoField(primary_key=True, serialize=False)),
                ('Title', models.CharField(max_length=100)),
                ('Picture', models.ImageField(blank=True, null=True, upload_to='category_images/%y/%m/%d')),
                ('Active', models.BooleanField(default=True)),
                ('Slug', models.SlugField(blank=True, null=True, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('ProductName', models.CharField(max_length=100)),
                ('ProductDescription', models.TextField()),
                ('QuantityPerUnit', models.CharField(max_length=50)),
                ('UnitPrice', models.DecimalField(decimal_places=2, max_digits=10)),
                ('UnitWeight', models.DecimalField(decimal_places=2, max_digits=5)),
                ('OutOfStock', models.BooleanField(default=False)),
                ('DiscountAvailable', models.BooleanField(default=False)),
                ('Discount', models.DecimalField(decimal_places=2, default=0.0, max_digits=5)),
                ('Reviews', models.TextField(blank=True, null=True)),
                ('Rating', models.DecimalField(decimal_places=2, default=5.0, max_digits=10, validators=[django.core.validators.MinValueValidator(0.0), django.core.validators.MaxValueValidator(5.0)])),
                ('Publish_Date', models.DateTimeField(auto_now_add=True)),
                ('Category', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='CatPro', to='products.category')),
                ('MatCategory', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='MatCatPro', to='products.matcategory')),
                ('Supplier', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='accounts.supplier')),
            ],
        ),
        migrations.CreateModel(
            name='ProColors',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Color', models.CharField(blank=True, max_length=20, null=True)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='Colors', to='products.product')),
            ],
        ),
        migrations.CreateModel(
            name='ProImage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(blank=True, default='', null=True, upload_to="product_images/%y/%m/%d'")),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='images', to='products.product')),
            ],
        ),
        migrations.CreateModel(
            name='ProSizes',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Size', models.CharField(blank=True, max_length=20, null=True)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='Sizes', to='products.product')),
            ],
        ),
    ]
