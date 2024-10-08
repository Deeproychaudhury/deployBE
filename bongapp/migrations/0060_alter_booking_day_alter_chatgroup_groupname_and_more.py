# Generated by Django 5.0.2 on 2024-08-12 07:58

import datetime
import django.db.models.deletion
import shortuuid.main
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bongapp', '0059_rename_airconditioning_hall_stage_alter_booking_day_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterField(
            model_name='booking',
            name='day',
            field=models.DateField(default=datetime.datetime(2024, 8, 12, 13, 28, 5, 687381)),
        ),
        migrations.AlterField(
            model_name='chatgroup',
            name='groupname',
            field=models.CharField(blank=True, default=shortuuid.main.ShortUUID.uuid, max_length=100, unique=True),
        ),
        migrations.CreateModel(
            name='HallBookings',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('booking_id', models.CharField(blank=True, default=shortuuid.main.ShortUUID.uuid, max_length=100, unique=True)),
                ('checkin', models.DateField()),
                ('checkout', models.DateField()),
                ('payment_status', models.BooleanField(default=False)),
                ('stripe_checkout_sessionid', models.CharField(blank=True, max_length=255, null=True)),
                ('Hall', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='bongapp.hall')),
                ('customer', models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
