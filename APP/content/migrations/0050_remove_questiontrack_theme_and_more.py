# Generated by Django 4.0.1 on 2023-07-27 21:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0049_questiontrack_theme'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='questiontrack',
            name='theme',
        ),
        migrations.AlterField(
            model_name='questiontrack',
            name='track_mark',
            field=models.IntegerField(choices=[('1', 'Easy'), ('2', 'Ok'), ('3', 'Hard')], null=True),
        ),
    ]
