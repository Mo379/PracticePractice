# Generated by Django 4.0.1 on 2022-08-31 19:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='organisation',
            name='location',
            field=models.TextField(blank=True, max_length=500),
        ),
    ]
