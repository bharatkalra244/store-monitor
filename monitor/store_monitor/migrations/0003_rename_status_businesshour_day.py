# Generated by Django 4.2.7 on 2023-11-06 19:24

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('store_monitor', '0002_alter_store_status'),
    ]

    operations = [
        migrations.RenameField(
            model_name='businesshour',
            old_name='status',
            new_name='day',
        ),
    ]
