# Generated by Django 4.0.1 on 2022-08-28 17:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0003_rename_date_of_brith_user_date_of_birth_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='account_details_complete',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='user',
            name='group_details_complete',
            field=models.BooleanField(default=False),
        ),
    ]