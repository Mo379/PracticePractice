# Generated by Django 4.0.1 on 2023-08-22 11:23

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0057_coursesubscription_monthly_significant_clicks'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='course',
            name='course_contributors',
        ),
    ]
