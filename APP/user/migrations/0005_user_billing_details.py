# Generated by Django 4.0.1 on 2022-08-28 18:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0004_user_account_details_complete_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='billing_details',
            field=models.BooleanField(default=False),
        ),
    ]
