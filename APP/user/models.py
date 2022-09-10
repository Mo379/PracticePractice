from django.conf import settings
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
    icon_id = models.CharField(max_length=30, default='', null=True)
    profile_upload = models.FileField(
            upload_to='uploads/profile_picture',
            blank=True
        )
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


class Organisation(models.Model):
    user = models.ForeignKey(
            User, on_delete=models.SET_NULL, null=True, db_index=True,
            related_name='Organisation'
        )
    name = models.CharField(max_length=30, default='', null=True)
    phone_number = models.CharField(max_length=15, default='', null=True)
    incorporation_date = models.DateField(null=True, blank=True)
    logo_upload = models.FileField(
            upload_to='uploads/organisation_logo',
            blank=True
        )
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


class Educator(models.Model):
    user = models.ForeignKey(
            User, on_delete=models.SET_NULL, null=True, db_index=True,
            related_name='Educator'
        )
    organisation_affiliation = models.ManyToManyField(
            Organisation, blank=True,
            related_name='educator_org_affiliation'
        )
    CHOICES_SUBJECTS = [(s, s) for s in settings.VALID_SUBJECTS]
    taught_subjects = MultiSelectField(
            choices=CHOICES_SUBJECTS,
            max_choices=len(CHOICES_SUBJECTS),
            max_length=sum([len(i[0]) for i in CHOICES_SUBJECTS])+50,
            default=[]
        )

    def __str__(self):
        return self.user.username if self.user else 'Unknown'


class Admin(models.Model):
    user = models.ForeignKey(
            User, on_delete=models.SET_NULL, null=True, db_index=True,
            related_name='Admin'
        )
    CHOICES_ROLES = [
        ('General', 'Fully Privileged Administrator'),
        ('Subject', 'Subject Specific Adminstrator'),
    ]
    roles = models.CharField(
        max_length=10,
        choices=CHOICES_ROLES,
        null=True
    )
    CHOICES_SUBJECTS = [(s, s) for s in settings.VALID_SUBJECTS]
    specialised_subjects = MultiSelectField(
            choices=CHOICES_SUBJECTS,
            max_choices=len(CHOICES_SUBJECTS),
            max_length=sum([len(i[0]) for i in CHOICES_SUBJECTS])+50,
            default=[]
        )

    approval_status = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username if self.user else 'Unknown' 


class Student(models.Model):
    user = models.ForeignKey(
            User, on_delete=models.SET_NULL, null=True, db_index=True,
            related_name='Student'
        )
    organisation_affiliation = models.ManyToManyField(
            Organisation, blank=True,
            related_name='student_org_affiliation'
        )
    educator_affiliation = models.ManyToManyField(
            Educator, blank=True,
            related_name='student_edu_affiliation'
        )
    CHOICES_SUBJECTS = [(s, s) for s in settings.VALID_SUBJECTS]
    studied_subjects = MultiSelectField(
            choices=CHOICES_SUBJECTS,
            max_choices=len(CHOICES_SUBJECTS),
            max_length=sum([len(i[0]) for i in CHOICES_SUBJECTS])+50,
            default=[]
        )

    def __str__(self):
        return self.user.username if self.user else 'Unknown' 


class Editor(models.Model):
    user = models.ForeignKey(
            User, on_delete=models.SET_NULL, null=True, db_index=True,
            related_name='Editor'
        )
    CHOICES_SUBJECTS = [(s, s) for s in settings.VALID_SUBJECTS]
    writing_subjects = MultiSelectField(
            choices=CHOICES_SUBJECTS,
            max_choices=len(CHOICES_SUBJECTS),
            max_length=sum([len(i[0]) for i in CHOICES_SUBJECTS])+50,
            default=[]
        )
    certification = models.FileField(
            upload_to='uploads/certification',
            blank=True
        )
    example_work = models.FileField(
            upload_to='uploads/examplework',
            blank=True
        )
    approval_status = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username if self.user else 'Unknown' 


class Affiliate(models.Model):
    user = models.ForeignKey(
            User, on_delete=models.SET_NULL, null=True, db_index=True,
            related_name='Affiliate'
        )
    platform_url = models.URLField(null=True, blank=True)
    approval_status = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username if self.user else 'Unknown' 
