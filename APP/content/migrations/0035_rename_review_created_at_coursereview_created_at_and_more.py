# Generated by Django 4.0.1 on 2023-05-06 08:37

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('content', '0034_coursesubscription_reviewed_review'),
    ]

    operations = [
        migrations.RenameField(
            model_name='coursereview',
            old_name='review_created_at',
            new_name='created_at',
        ),
        migrations.RenameField(
            model_name='coursereview',
            old_name='review_stars',
            new_name='rating',
        ),
        migrations.RemoveField(
            model_name='coursereview',
            name='review_text',
        ),
        migrations.AddField(
            model_name='coursereview',
            name='review',
            field=models.TextField(default='', max_length=2500, null=True),
        ),
        migrations.AlterField(
            model_name='coursereview',
            name='course',
            field=models.ForeignKey(default='', null=True, on_delete=django.db.models.deletion.CASCADE, to='content.course'),
        ),
        migrations.AlterField(
            model_name='coursereview',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.DeleteModel(
            name='Review',
        ),
    ]
