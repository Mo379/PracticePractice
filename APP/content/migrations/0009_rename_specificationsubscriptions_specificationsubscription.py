# Generated by Django 4.0.1 on 2022-10-18 06:44

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('content', '0008_specificationsubscriptions'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='SpecificationSubscriptions',
            new_name='SpecificationSubscription',
        ),
    ]