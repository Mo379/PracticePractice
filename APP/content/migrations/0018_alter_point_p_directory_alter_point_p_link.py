# Generated by Django 4.0.1 on 2022-04-06 10:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0017_remove_question_q_level_point_p_chapter_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='point',
            name='p_directory',
            field=models.CharField(default='', max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='point',
            name='p_link',
            field=models.CharField(default='', max_length=255, null=True),
        ),
    ]