# Generated by Django 4.0.1 on 2023-08-16 12:10

import collections
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0056_userpaper_percentage_score'),
    ]

    operations = [
        migrations.AddField(
            model_name='coursesubscription',
            name='monthly_significant_clicks',
            field=models.JSONField(default=collections.OrderedDict, null=True),
        ),
    ]
