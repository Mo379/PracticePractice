# Generated by Django 4.0.1 on 2022-11-26 10:19

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0012_course_course_contributors_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='coursereview',
            name='review_created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]