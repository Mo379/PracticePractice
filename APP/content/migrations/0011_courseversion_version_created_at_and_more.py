# Generated by Django 4.0.1 on 2022-11-23 13:41

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0010_course_course_created_at_course_course_updated_at_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='courseversion',
            name='version_created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='courseversion',
            name='version_updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
    ]