# Generated by Django 4.0.1 on 2023-04-07 12:32

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('AI', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='lesson',
            old_name='conditions',
            new_name='lesson_chat',
        ),
    ]
