# Generated by Django 4.0.1 on 2023-04-26 08:24

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0027_remove_question_q_board_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='question',
            name='q_total_marks',
        ),
    ]