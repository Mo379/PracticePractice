# Generated by Django 4.0.1 on 2023-05-27 13:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0043_question_q_mdcontent_ans'),
    ]

    operations = [
        migrations.AddField(
            model_name='question',
            name='q_videos',
            field=models.ManyToManyField(to='content.Video'),
        ),
    ]
