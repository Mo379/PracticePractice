# Generated by Django 4.0.1 on 2022-05-29 10:56

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0008_rename_registration_userprofile_registered_status'),
    ]

    operations = [
        migrations.RenameField(
            model_name='userprofile',
            old_name='registered_status',
            new_name='registration',
        ),
    ]
