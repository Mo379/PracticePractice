# Generated by Django 4.0.1 on 2022-12-06 13:52

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0016_question_q_mdcontent'),
    ]

    operations = [
        migrations.DeleteModel(
            name='ContentTemplate',
        ),
        migrations.RemoveField(
            model_name='point',
            name='p_MDcontent',
        ),
        migrations.RemoveField(
            model_name='question',
            name='q_MDcontent',
        ),
    ]
