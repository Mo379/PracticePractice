# Generated by Django 4.0.1 on 2023-04-07 15:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('AI', '0003_alter_lesson_moduel'),
    ]

    operations = [
        migrations.AddField(
            model_name='lesson',
            name='lesson_content',
            field=models.JSONField(default=dict, null=True),
        ),
    ]
