from django.utils import timezone
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save
from django.dispatch import receiver


# Create your models here.
class User(AbstractUser):
    registration = models.BooleanField(default=False)
    password_set = models.BooleanField(default=True)
    is_member = models.BooleanField(default=False)
    bio = models.TextField(max_length=500, blank=True)
    Date_of_brith = models.DateField(null=True, blank=True)

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


class Teacher(models.Model):
    user = models.ForeignKey(
            User, on_delete=models.SET_NULL, null=True, db_index=True,
            related_name='Teacher'
        )

    def __str__(self):
        return self.username


class PrivateTutor(models.Model):
    user = models.ForeignKey(
            User, on_delete=models.SET_NULL, null=True, db_index=True,
            related_name='PrivateTutor'
        )

    def __str__(self):
        return self.username



class School(models.Model):
    user = models.ForeignKey(
            User, on_delete=models.SET_NULL, null=True, db_index=True,
            related_name='School'
        )

    def __str__(self):
        return self.username



class TuitionCenter(models.Model):
    user = models.ForeignKey(
            User, on_delete=models.SET_NULL, null=True, db_index=True,
            related_name='TuitionCenter'
        )

    def __str__(self):
        return self.username



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
