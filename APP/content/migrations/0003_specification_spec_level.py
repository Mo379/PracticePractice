# Generated by Django 4.0.1 on 2022-11-15 14:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0002_remove_specification_spec_level_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='specification',
            name='spec_level',
            field=models.CharField(default='', max_length=50, null=True),
        ),
    ]