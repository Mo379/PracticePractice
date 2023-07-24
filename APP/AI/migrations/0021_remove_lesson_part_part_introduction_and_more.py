# Generated by Django 4.0.1 on 2023-05-21 15:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('AI', '0020_remove_contentgenerationjob_started'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='lesson_part',
            name='part_introduction',
        ),
        migrations.RemoveField(
            model_name='lesson_part',
            name='part_pointer',
        ),
        migrations.AddField(
            model_name='lesson',
            name='lesson_introduction',
            field=models.TextField(default='', null=True),
        ),
    ]