# Generated by Django 4.0.1 on 2022-11-20 10:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0006_courseversion_version_note'),
    ]

    operations = [
        migrations.AddField(
            model_name='courseversion',
            name='version_number',
            field=models.PositiveSmallIntegerField(null=True),
        ),
    ]
