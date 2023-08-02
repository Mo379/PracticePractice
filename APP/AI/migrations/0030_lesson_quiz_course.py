# Generated by Django 4.0.1 on 2023-08-01 18:52

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0054_alter_question_q_marks'),
        ('AI', '0029_alter_lesson_part_part_chat'),
    ]

    operations = [
        migrations.AddField(
            model_name='lesson_quiz',
            name='course',
            field=models.ForeignKey(default='', on_delete=django.db.models.deletion.CASCADE, related_name='AI_quiz_course', to='content.course'),
        ),
    ]
