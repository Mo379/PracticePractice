# Generated by Django 4.0.1 on 2022-10-03 14:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0005_alter_question_q_board_moduel'),
    ]

    operations = [
        migrations.AddField(
            model_name='point',
            name='p_number',
            field=models.IntegerField(default=-1, null=True),
        ),
    ]
