# Generated by Django 4.0.1 on 2022-12-12 13:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0010_alter_questiontrack_course'),
    ]

    operations = [
        migrations.AddField(
            model_name='questiontrack',
            name='track_mark_boolean',
            field=models.BooleanField(default=False, null=True),
        ),
    ]
