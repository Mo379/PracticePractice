# Generated by Django 4.0.1 on 2022-09-04 12:36

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0008_rename_subjects_student_studied_subjects'),
    ]

    operations = [
        migrations.RenameField(
            model_name='admin',
            old_name='subjects',
            new_name='specialised_subjects',
        ),
    ]