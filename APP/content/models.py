from django.db import models

# Create your models here.
class Questions(models.Model):
    object_unique_id = models.CharField(max_length=50)
    link = models.CharField(max_length=255)
    data = models.JSONField()
class Points(models.Model):
    object_unique_id = models.CharField(max_length=50)
    link = models.CharField(max_length=255)
    data = models.JSONField()
class Specifications(models.Model):
    name = models.CharField(max_length=50)
    subject = models.CharField(max_length=50)
    level = models.CharField(max_length=50)
    board = models.CharField(max_length=50)
    year = models.CharField(max_length=50)
    structure = models.JSONField()
