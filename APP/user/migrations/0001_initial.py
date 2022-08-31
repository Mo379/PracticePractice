# Generated by Django 4.0.1 on 2022-08-31 19:53

from django.conf import settings
import django.contrib.auth.models
import django.contrib.auth.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import multiselectfield.db.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('registration', models.BooleanField(default=False)),
                ('password_set', models.BooleanField(default=True)),
                ('account_details_complete', models.BooleanField(default=False)),
                ('group_details_complete', models.BooleanField(default=False)),
                ('is_member', models.BooleanField(default=False)),
                ('billing_details', models.BooleanField(default=False)),
                ('verification_status', models.BooleanField(default=False)),
                ('bio', models.TextField(blank=True, max_length=500)),
                ('date_of_birth', models.DateField(blank=True, null=True)),
                ('Icon_id', models.CharField(default='', max_length=30, null=True)),
                ('theme', models.CharField(choices=[('lig', 'Light'), ('dar', 'Dark'), ('lib', 'Library')], default='lig', max_length=3)),
                ('language', models.CharField(choices=[('en', 'English'), ('fr', 'French'), ('es', 'Spanish')], default='en', max_length=2)),
                ('mail_choices', multiselectfield.db.fields.MultiSelectField(choices=[('GroupChange', "Changes made to groups you're part of."), ('ProductUpdate', "Product updates for products you've purchased or starred."), ('New', 'Information on new products and service.'), ('Marketing', 'Marketing and promotional offers.'), ('Core', 'Core Emails. (This is mandatory)')], default=['GroupChange', 'ProductUpdate', 'New', 'Marketing', 'Core'], max_length=90)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Student',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='Student', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Organisation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='', max_length=30, null=True)),
                ('phone_number', models.CharField(default='', max_length=15, null=True)),
                ('incorporation_date', models.DateField(blank=True, null=True)),
                ('icon_id', models.CharField(default='', max_length=30, null=True)),
                ('url', models.URLField(blank=True, null=True)),
                ('is_active', models.BooleanField(default=False)),
                ('n_managers', models.IntegerField(default=1, null=True)),
                ('n_classes', models.IntegerField(default=0, null=True)),
                ('n_teachers', models.IntegerField(default=0, null=True)),
                ('n_students', models.IntegerField(default=0, null=True)),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='Organisation', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Educator',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='Educator', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Editor',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='Editor', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Affiliate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='Affiliate', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Admin',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='Admin', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
