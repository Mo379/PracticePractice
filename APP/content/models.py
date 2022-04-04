from django.db import models

# Create your models here.
class Question(models.Model):
    q_subject = models.CharField(max_length=50)
    def __str__(self):
        return self.q_subject
class Point(models.Model):
    p_subject = models.CharField(max_length=50)
    def __str__(self):
        return self.p_subject
class Video(models.Model):
    v_title = models.CharField(max_length=50)
    def __str__(self):
        return self.v_title
