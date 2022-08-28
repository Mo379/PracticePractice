# Generated by Django 4.0.1 on 2022-08-28 12:14

from django.db import migrations
import multiselectfield.db.fields


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='mail_choices',
            field=multiselectfield.db.fields.MultiSelectField(choices=[('AccountChange', 'AccountChange'), ('GroupChange', 'GroupChange'), ('ProductUpdate', 'ProductUpdate'), ('New', 'New'), ('Marketing', 'Marketing'), ('Core', 'Core')], default=['AccountChange', 'GroupChange', 'ProductUpdate', 'New', 'Marketing', 'Core'], max_length=103),
        ),
    ]