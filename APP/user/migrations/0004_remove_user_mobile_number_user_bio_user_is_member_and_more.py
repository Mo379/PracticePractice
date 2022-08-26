# Generated by Django 4.0.1 on 2022-08-26 15:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0003_alter_userprofile_is_member'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='mobile_number',
        ),
        migrations.AddField(
            model_name='user',
            name='bio',
            field=models.TextField(blank=True, max_length=500),
        ),
        migrations.AddField(
            model_name='user',
            name='is_member',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='user',
            name='password_set',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='user',
            name='registration',
            field=models.BooleanField(default=False),
        ),
        migrations.DeleteModel(
            name='UserProfile',
        ),
    ]
