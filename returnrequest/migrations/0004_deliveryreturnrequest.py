# Generated by Django 5.0.3 on 2024-06-27 21:19

import django.db.models.deletion
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('returnrequest', '0003_alter_returnrequest_initial_status_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='DeliveryReturnRequest',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('accepted_at', models.DateTimeField(auto_now_add=True)),
                ('ReturnRequest', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='delivery_ReturnRequest', to='returnrequest.returnrequest')),
                ('delivery_person', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='delivery_ReturnRequest', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
