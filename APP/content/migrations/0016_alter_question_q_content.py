# Generated by Django 4.0.1 on 2022-04-06 01:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0015_question_q_content_alter_question_q_exam_month'),
    ]

    operations = [
        migrations.AlterField(
            model_name='question',
            name='q_content',
            field=models.JSONField(default=dict, null=True),
        ),
    ]