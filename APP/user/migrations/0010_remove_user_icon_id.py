# Generated by Django 4.0.1 on 2022-12-02 17:12

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0009_remove_user_group_details_complete'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='icon_id',
        ),
    ]
