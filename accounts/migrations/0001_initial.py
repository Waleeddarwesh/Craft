# Generated by Django 5.0.3 on 2024-04-29 16:28

import django.core.validators
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('id', models.BigAutoField(editable=False, primary_key=True, serialize=False)),
                ('email', models.EmailField(max_length=255, unique=True, verbose_name='Email Address')),
                ('first_name', models.CharField(max_length=100, verbose_name='First Name')),
                ('last_name', models.CharField(max_length=100, verbose_name='Last Name')),
                ('PhoneNO', models.CharField(max_length=14, verbose_name='Phone number')),
                ('is_staff', models.BooleanField(default=False)),
                ('is_superuser', models.BooleanField(default=False)),
                ('is_verified', models.BooleanField(default=False)),
                ('is_active', models.BooleanField(default=True)),
                ('date_joined', models.DateTimeField(auto_now_add=True)),
                ('last_login', models.DateTimeField(auto_now=True)),
                ('is_customer', models.BooleanField(default=False)),
                ('is_supplier', models.BooleanField(default=False)),
                ('is_delivery', models.BooleanField(default=False)),
                ('last_password_reset_request', models.DateTimeField(blank=True, null=True)),
                ('auth_provider', models.CharField(default='email', max_length=50)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Customer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('CustomerPhoto', models.ImageField(blank=True, null=True, upload_to='customer_photos/%y/%m/%d')),
                ('BuildingNO', models.CharField(max_length=10)),
                ('Street', models.CharField(max_length=100)),
                ('City', models.CharField(max_length=100)),
                ('State', models.CharField(max_length=100)),
                ('CreditCardNO', models.CharField(blank=True, max_length=20, null=True)),
                ('CreditCardType', models.CharField(blank=True, max_length=50, null=True)),
                ('CreditCardMonth', models.CharField(blank=True, max_length=2, null=True)),
                ('CreditCardYear', models.CharField(blank=True, max_length=4, null=True)),
                ('CreditCVV', models.CharField(max_length=3)),
                ('Balance', models.DecimalField(decimal_places=2, default=0.0, max_digits=10)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Delivery',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('DeliveryPhoto', models.ImageField(upload_to='shipper_photos/%y/%m/%d')),
                ('WithdrawMethod', models.CharField(choices=[('Vodafone Cash', 'Vodafone Cash'), ('Instapay', 'Instapay'), ('Bank Transfer', 'Bank Transfer'), ('Paypal', 'Paypal')], max_length=100)),
                ('WithdrawNO', models.CharField(max_length=100)),
                ('Balance', models.DecimalField(decimal_places=2, default=0.0, max_digits=10)),
                ('DeliveryContract', models.ImageField(upload_to='shipper_contracts/%y/%m/%d')),
                ('DeliveryIdentity', models.ImageField(upload_to='shipper_identities/%y/%m/%d')),
                ('VehicleModel', models.CharField(max_length=100)),
                ('VehicleColor', models.CharField(blank=True, max_length=100, null=True)),
                ('plateNO', models.CharField(max_length=100)),
                ('Rating', models.DecimalField(decimal_places=2, default=5.0, max_digits=10, validators=[django.core.validators.MinValueValidator(0.0), django.core.validators.MaxValueValidator(5.0)])),
                ('Orders', models.IntegerField(blank=True, null=True)),
                ('ExperienceYears', models.IntegerField(blank=True, null=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='delivery', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='OneTimePassword',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('otp', models.CharField(max_length=6)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Supplier',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('SupplierPhoto', models.ImageField(blank=True, null=True, upload_to='supplier_photos/%y/%m/%d')),
                ('SupplierCover', models.ImageField(blank=True, null=True, upload_to='supplier_covers/%y/%m/%d')),
                ('CategoryTitle', models.CharField(max_length=50)),
                ('BuildingNO', models.CharField(blank=True, max_length=10, null=True)),
                ('Street', models.CharField(blank=True, max_length=100, null=True)),
                ('City', models.CharField(blank=True, max_length=50, null=True)),
                ('State', models.CharField(blank=True, max_length=50, null=True)),
                ('WithdrawMethod', models.CharField(choices=[('Vodafone Cash', 'Vodafone Cash'), ('Instapay', 'Instapay'), ('Bank Transfer', 'Bank Transfer'), ('Paypal', 'Paypal')], max_length=100)),
                ('WithdrawNO', models.CharField(max_length=100)),
                ('Balance', models.DecimalField(decimal_places=2, default=0.0, max_digits=10)),
                ('CreditCardNO', models.CharField(blank=True, max_length=16, null=True)),
                ('CreditCardType', models.CharField(blank=True, max_length=20, null=True)),
                ('CreditCardMonth', models.IntegerField(blank=True, null=True)),
                ('CreditCardYear', models.IntegerField(blank=True, null=True)),
                ('CreditCVV', models.IntegerField(blank=True, null=True)),
                ('DiscountVouchers', models.TextField(blank=True, null=True)),
                ('currentOrders', models.IntegerField(blank=True, null=True)),
                ('Logo', models.ImageField(blank=True, null=True, upload_to='supplier_logos/%y/%m/%d')),
                ('SupplierContract', models.ImageField(upload_to='supplier_contracts/%y/%m/%d')),
                ('SupplierIdentity', models.ImageField(upload_to='supplier_identities/%y/%m/%d')),
                ('FollowersNo', models.IntegerField(default=0)),
                ('ExperienceYears', models.IntegerField(blank=True, null=True)),
                ('Rating', models.DecimalField(decimal_places=2, default=5.0, max_digits=10, validators=[django.core.validators.MinValueValidator(0.0), django.core.validators.MaxValueValidator(5.0)])),
                ('Orders', models.IntegerField(blank=True, null=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Follow',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounts.customer')),
                ('Supplier', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounts.supplier')),
            ],
            options={
                'unique_together': {('Customer', 'Supplier')},
            },
        ),
    ]