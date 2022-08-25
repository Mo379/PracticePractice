# Generated by Django 4.0.1 on 2022-08-25 10:49

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('content', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='userpaper',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='questiontrack',
            name='question',
            field=models.ForeignKey(db_column='q_unique_id', on_delete=django.db.models.deletion.CASCADE, to='content.question'),
        ),
        migrations.AddField(
            model_name='questiontrack',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='editingtask',
            name='task_editor',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
