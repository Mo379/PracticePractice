# Generated by Django 4.0.1 on 2022-11-20 10:08

import collections
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0004_course_user'),
    ]

    operations = [
        migrations.CreateModel(
            name='CourseVersion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('version_name', models.CharField(default='', max_length=150, null=True)),
                ('version_content', models.JSONField(default=collections.OrderedDict, null=True)),
                ('version_publication', models.BooleanField(default=False, null=True)),
                ('deleted', models.BooleanField(default=False, null=True)),
                ('course', models.ForeignKey(default='', null=True, on_delete=django.db.models.deletion.CASCADE, to='content.course')),
            ],
        ),
    ]
