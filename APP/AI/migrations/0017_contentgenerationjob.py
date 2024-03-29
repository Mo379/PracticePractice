# Generated by Django 4.0.1 on 2023-05-08 09:58

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0036_rename_created_at_coursereview_review_created_at_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('AI', '0016_remove_contentpromptpoint_point_number_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='ContentGenerationJob',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('moduel', models.CharField(default='', max_length=255, null=True)),
                ('chapter', models.CharField(default='', max_length=255, null=True)),
                ('model', models.CharField(default='', max_length=150, null=True)),
                ('prompt', models.IntegerField(default=0, null=True)),
                ('completion', models.IntegerField(default=0, null=True)),
                ('total', models.IntegerField(default=0, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('specification', models.ForeignKey(default='', on_delete=django.db.models.deletion.CASCADE, related_name='AI_contentjob', to='content.specification')),
                ('user', models.ForeignKey(default='', on_delete=django.db.models.deletion.CASCADE, related_name='AI_contentgeneration_user', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
