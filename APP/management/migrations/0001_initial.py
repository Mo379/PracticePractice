# Generated by Django 4.0.1 on 2022-08-25 10:48

from django.db import migrations
from management.initial_perms import populate_groups ## NEW



class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.RunPython(populate_groups)
    ]
