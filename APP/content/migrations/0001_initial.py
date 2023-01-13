# Generated by Django 4.0.1 on 2023-01-11 13:06

import collections
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import mdeditor.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ContentTemplate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='', max_length=50, null=True)),
                ('content', models.JSONField(default=collections.OrderedDict, null=True)),
                ('MDcontent', mdeditor.fields.MDTextField(default='', null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Course',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('course_name', models.CharField(default='', max_length=150, null=True)),
                ('course_summary', models.TextField(default='', max_length=1000, null=True)),
                ('course_skills', models.JSONField(default=collections.OrderedDict, null=True)),
                ('course_learning_objectives', models.JSONField(default=collections.OrderedDict, null=True)),
                ('course_contributors', models.JSONField(default=collections.OrderedDict, null=True)),
                ('course_language', models.CharField(default='', max_length=150, null=True)),
                ('course_level', models.CharField(default='', max_length=150, null=True)),
                ('course_question_bank_only', models.BooleanField(default=False, null=True)),
                ('course_estimated_time', models.CharField(default='', max_length=150, null=True)),
                ('course_created_at', models.DateTimeField(auto_now_add=True)),
                ('course_updated_at', models.DateTimeField(auto_now=True)),
                ('course_publication', models.BooleanField(default=False, null=True)),
                ('course_pic_ext', models.CharField(default='', max_length=150, null=True)),
                ('course_pic_status', models.BooleanField(default=False)),
                ('deleted', models.BooleanField(default=False, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Question',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('q_in_house', models.BooleanField(default=False, null=True)),
                ('q_level', models.CharField(default='', max_length=30, null=True)),
                ('q_board', models.CharField(default='', max_length=10, null=True)),
                ('q_board_moduel', models.CharField(default='', max_length=50, null=True)),
                ('q_exam_month', models.IntegerField(default=0, null=True)),
                ('q_exam_year', models.IntegerField(default=0, null=True)),
                ('q_is_exam', models.BooleanField(default=False, null=True)),
                ('q_exam_num', models.IntegerField(default=0, null=True)),
                ('q_subject', models.CharField(default='', max_length=50, null=True)),
                ('q_moduel', models.CharField(default='', max_length=50, null=True)),
                ('q_chapter', models.CharField(default='', max_length=50, null=True)),
                ('q_topic', models.CharField(default='', max_length=50, null=True)),
                ('q_type', models.CharField(default='', max_length=50, null=True)),
                ('q_difficulty', models.IntegerField(default=0, null=True)),
                ('q_total_marks', models.IntegerField(default=0, null=True)),
                ('q_content', models.JSONField(default=dict, null=True)),
                ('q_MDcontent', mdeditor.fields.MDTextField(default='', null=True)),
                ('q_files_directory', models.CharField(default='', max_length=255, null=True)),
                ('q_unique_id', models.CharField(db_index=True, default='', max_length=11, null=True, unique=True)),
                ('deleted', models.BooleanField(default=False, null=True)),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='UserPaper',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pap_info', models.JSONField(default=dict, null=True)),
                ('pap_creation_time', models.DateTimeField(auto_now_add=True, verbose_name='date created')),
                ('pap_completion', models.BooleanField(default=False, null=True)),
                ('deleted', models.BooleanField(default=False, null=True)),
                ('pap_course', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='content.course')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Specification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('spec_in_house', models.BooleanField(default=False, null=True)),
                ('spec_level', models.CharField(default='', max_length=50, null=True)),
                ('spec_subject', models.CharField(default='', max_length=50, null=True)),
                ('spec_board', models.CharField(default='', max_length=50, null=True)),
                ('spec_name', models.CharField(default='', max_length=50, null=True)),
                ('spec_first_assessment', models.DateTimeField(blank=True, null=True, verbose_name='First assessment')),
                ('spec_last_assessment', models.DateTimeField(blank=True, null=True, verbose_name='Last assessment')),
                ('spec_content', models.JSONField(default=collections.OrderedDict, null=True)),
                ('spec_completion', models.BooleanField(default=False, null=True)),
                ('deleted', models.BooleanField(default=False, null=True)),
                ('user', models.ForeignKey(default='', null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='QuestionTrack',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('track_mark', models.IntegerField(default=0, null=True)),
                ('track_mark_boolean', models.BooleanField(default=False, null=True)),
                ('track_attempt_number', models.IntegerField(default=0, null=True)),
                ('track_creation_time', models.DateTimeField(auto_now_add=True, verbose_name='date created')),
                ('course', models.ForeignKey(db_column='specification', on_delete=django.db.models.deletion.CASCADE, to='content.course')),
                ('question', models.ForeignKey(db_column='q_unique_id', on_delete=django.db.models.deletion.CASCADE, to='content.question')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Point',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('p_in_house', models.BooleanField(default=False, null=True)),
                ('p_level', models.CharField(default='', max_length=50, null=True)),
                ('p_subject', models.CharField(default='', max_length=255, null=True)),
                ('p_moduel', models.CharField(default='', max_length=255, null=True)),
                ('p_chapter', models.CharField(default='', max_length=255, null=True)),
                ('p_topic', models.CharField(default='', max_length=255, null=True)),
                ('p_number', models.IntegerField(default=-1, null=True)),
                ('p_content', models.JSONField(default=dict, null=True)),
                ('p_MDcontent', mdeditor.fields.MDTextField(default='', null=True)),
                ('p_files_directory', models.CharField(default='', max_length=255, null=True)),
                ('p_unique_id', models.CharField(db_index=True, default='', max_length=11, null=True, unique=True)),
                ('deleted', models.BooleanField(default=False, null=True)),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Keyword',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('kw_word', models.CharField(max_length=50, null=True)),
                ('kw_definition', models.CharField(max_length=255, null=True)),
                ('specification', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='content.specification')),
            ],
        ),
        migrations.CreateModel(
            name='EditingTask',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('task_moduel', models.CharField(default='', max_length=255, null=True)),
                ('task_chapter', models.CharField(default='', max_length=255, null=True)),
                ('task_topic', models.CharField(default='', max_length=255, null=True)),
                ('task_payment_amount', models.DecimalField(decimal_places=2, max_digits=6)),
                ('task_completion_status', models.BooleanField(default=False, null=True)),
                ('task_approval_status', models.BooleanField(default=False, null=True)),
                ('specification', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='content.specification')),
                ('task_editor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='CourseVersion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('version_number', models.PositiveSmallIntegerField(null=True)),
                ('version_name', models.CharField(default='', max_length=150, null=True)),
                ('version_content', models.JSONField(default=collections.OrderedDict, null=True)),
                ('version_note', models.CharField(default='', max_length=255, null=True)),
                ('version_publication', models.BooleanField(default=False, null=True)),
                ('version_created_at', models.DateTimeField(auto_now_add=True)),
                ('version_updated_at', models.DateTimeField(auto_now=True)),
                ('deleted', models.BooleanField(default=False, null=True)),
                ('course', models.ForeignKey(default='', null=True, on_delete=django.db.models.deletion.CASCADE, to='content.course')),
            ],
        ),
        migrations.CreateModel(
            name='CourseSubscription',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('subscription_created_at', models.DateTimeField(auto_now_add=True)),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='content.course')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='CourseReview',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('review_stars', models.PositiveSmallIntegerField(null=True)),
                ('review_text', models.CharField(default='', max_length=255, null=True)),
                ('review_created_at', models.DateTimeField(auto_now_add=True)),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='content.course')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='course',
            name='specification',
            field=models.ForeignKey(default='', null=True, on_delete=django.db.models.deletion.CASCADE, to='content.specification'),
        ),
        migrations.AddField(
            model_name='course',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
