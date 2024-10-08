# Generated by Django 5.0.2 on 2024-08-23 14:35

import cloudinary_storage.storage
import shortuuid.main
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bongapp', '0084_alter_chatgroup_groupname_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='YourImageModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(storage=cloudinary_storage.storage.MediaCloudinaryStorage(), upload_to='')),
            ],
        ),
        migrations.CreateModel(
            name='YourRawFileModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(storage=cloudinary_storage.storage.RawMediaCloudinaryStorage(), upload_to='')),
            ],
        ),
        migrations.CreateModel(
            name='YourVideoModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('video', models.FileField(storage=cloudinary_storage.storage.VideoMediaCloudinaryStorage(), upload_to='')),
            ],
        ),
        migrations.AlterField(
            model_name='chatgroup',
            name='groupname',
            field=models.CharField(blank=True, default=shortuuid.main.ShortUUID.uuid, max_length=100, unique=True),
        ),
        migrations.AlterField(
            model_name='hallbookings',
            name='booking_id',
            field=models.CharField(blank=True, default=shortuuid.main.ShortUUID.uuid, max_length=100, unique=True),
        ),
    ]
