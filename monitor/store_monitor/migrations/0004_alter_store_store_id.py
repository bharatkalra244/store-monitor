# Generated by Django 4.2.7 on 2023-11-06 19:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store_monitor', '0003_rename_status_businesshour_day'),
    ]

    operations = [
        migrations.AlterField(
            model_name='store',
            name='store_id',
            field=models.BigIntegerField(unique=True),
        ),
    ]
