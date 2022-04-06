from django.db import models

# Create your models here.
class Question(models.Model):
    #
    q_level = models.CharField(max_length=10, default='',null=True) 
    q_board = models.CharField(max_length=10, default='',null=True)  
    q_board_moduel = models.CharField(max_length=10, default='',null=True) 
    q_exam_month = models.IntegerField(default=0,null=True) 
    q_exam_year = models.IntegerField(default=0,null=True)
    q_is_exam= models.BooleanField(default=False,null=True)
    q_exam_num= models.IntegerField(default=0,null=True)
    #
    q_subject = models.CharField(max_length=50, default='',null=True)
    q_moduel= models.CharField(max_length=50,default='',null=True)
    q_chapter= models.CharField(max_length=50,default='',null=True)
    q_topic= models.CharField(max_length=50,default='',null=True)
    #
    q_type = models.CharField(max_length=50,default='',null=True) 
    q_difficulty = models.IntegerField(default=0,null=True) 
    q_total_marks= models.IntegerField(default=0,null=True) 
    q_content= models.JSONField(default = dict,null=True) 
    q_dir= models.CharField(max_length=255,default='',null=True)
    q_link = models.CharField(max_length=255,default='',null=True)
    q_unique_id= models.CharField(max_length=11, db_index=True,default='',null=True,unique=True)
    def __str__(self):
        return self.q_unique_id
class Point(models.Model):
    p_subject = models.CharField(max_length=50)
    def __str__(self):
        return self.p_subject
class Video(models.Model):
    v_title = models.CharField(max_length=50)
    def __str__(self):
        return self.v_title
