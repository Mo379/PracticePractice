# Generated by Django 4.0.1 on 2023-06-01 21:19

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0047_image_in_question_placement'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='video',
            name='placement',
        ),
    ]
