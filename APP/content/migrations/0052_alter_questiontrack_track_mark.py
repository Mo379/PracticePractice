# Generated by Django 4.0.1 on 2023-07-27 22:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0051_remove_questiontrack_track_mark_boolean'),
    ]

    operations = [
        migrations.AlterField(
            model_name='questiontrack',
            name='track_mark',
            field=models.CharField(choices=[('1', 'Easy'), ('2', 'Ok'), ('3', 'Hard')], max_length=1, null=True),
        ),
    ]