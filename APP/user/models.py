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
    account_details_complete = models.BooleanField(default=False, null=True)
    is_member = models.BooleanField(default=False)
    bio = models.TextField(max_length=500, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    profile_pic_ext = models.CharField(max_length=50, default='', null=True)
    profile_pic_status = models.BooleanField(default=False) 
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


