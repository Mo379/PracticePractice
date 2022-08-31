from django.utils import timezone
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save
from django.dispatch import receiver
from multiselectfield import MultiSelectField


# Create your models here.
class User(AbstractUser):
    registration = models.BooleanField(default=False)
    password_set = models.BooleanField(default=True)
    account_details_complete = models.BooleanField(default=False)
    group_details_complete = models.BooleanField(default=False)
    is_member = models.BooleanField(default=False)
    billing_details = models.BooleanField(default=False)
    verification_status = models.BooleanField(default=False)
    bio = models.TextField(max_length=500, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    Icon_id = models.CharField(max_length=30, default='', null=True)
    #
    CHOICES_THEME = [
        ('lig', 'Light'),
        ('dar', 'Dark'),
        ('lib', 'Library'),
    ]
    theme = models.CharField(
        max_length=3,
        choices=CHOICES_THEME,
        default='lig',
    )
    CHOICES_LANGUAGE = [
        ('en', 'English'),
        ('fr', 'French'),
        ('es', 'Spanish'),
    ]
    language = models.CharField(
        max_length=2,
        choices=CHOICES_LANGUAGE,
        default='en',
    )
    CHOICES_EMAIL = [
        ('GroupChange', "Changes made to groups you're part of."),
        ('ProductUpdate', "Product updates for products you've purchased or starred."),
        ('New', "Information on new products and service."),
        ('Marketing', "Marketing and promotional offers."),
        ('Core', "Core Emails. (This is mandatory)"),
    ]
    mail_choices = MultiSelectField(
            choices=CHOICES_EMAIL,
            max_choices=len(CHOICES_EMAIL),
            max_length=sum([len(i[0]) for i in CHOICES_EMAIL])+50,
            default=[i[0] for i in CHOICES_EMAIL]
        )

    def __str__(self):
        return self.username


class Admin(models.Model):
    user = models.ForeignKey(
            User, on_delete=models.SET_NULL, null=True, db_index=True,
            related_name='Admin'
        )

    def __str__(self):
        return self.username


class Student(models.Model):
    user = models.ForeignKey(
            User, on_delete=models.SET_NULL, null=True, db_index=True,
            related_name='Student'
        )

    def __str__(self):
        return self.username


class Educator(models.Model):
    user = models.ForeignKey(
            User, on_delete=models.SET_NULL, null=True, db_index=True,
            related_name='Educator'
        )

    def __str__(self):
        return self.username


class Organisation(models.Model):
    user = models.ForeignKey(
            User, on_delete=models.SET_NULL, null=True, db_index=True,
            related_name='Organisation'
        )
    name = models.CharField(max_length=30, default='', null=True)
    phone_number = models.CharField(max_length=15, default='', null=True)
    incorporation_date = models.DateField(null=True, blank=True)
    icon_id = models.CharField(max_length=30, default='', null=True)
    url = models.URLField(null=True, blank=True)
    location = models.TextField(max_length=500, blank=True)
    is_active = models.BooleanField(default=False)
    n_managers = models.IntegerField(default=1, null=True)
    n_classes = models.IntegerField(default=0, null=True)
    n_teachers = models.IntegerField(default=0, null=True)
    n_students = models.IntegerField(default=0, null=True)
    #

    def __str__(self):
        return self.name


class Editor(models.Model):
    user = models.ForeignKey(
            User, on_delete=models.SET_NULL, null=True, db_index=True,
            related_name='Editor'
        )

    def __str__(self):
        return self.username


class Affiliate(models.Model):
    user = models.ForeignKey(
            User, on_delete=models.SET_NULL, null=True, db_index=True,
            related_name='Affiliate'
        )

    def __str__(self):
        return self.username
