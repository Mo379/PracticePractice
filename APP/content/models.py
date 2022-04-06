from django.utils import timezone
from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class Question(models.Model):
    #
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
class QuestionTrack(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,db_index=True)
    question = models.ForeignKey(Question, on_delete=models.CASCADE, 
            db_column='q_unique_id', db_index=True)
    track_mark = models.IntegerField(default=0,null=True) 
    track_creation_time = models.DateTimeField('date created', auto_now_add=True, blank=True)
    def __str__(self):
        return self.user
class UserPaper(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, db_index=True)
    pap_subject= models.CharField(max_length=50, default='')
    pap_info = models.JSONField(default=dict,null=True)
    pap_creation_time = models.DateTimeField('date created', auto_now_add=True, blank=True)
    def __str__(self):
        return self.pap_subject










class Point(models.Model):
    p_subject = models.CharField(max_length=255,default='',null=True)
    p_moduel= models.CharField(max_length=255,default='',null=True)
    p_chapter= models.CharField(max_length=255,default='',null=True)
    p_topic= models.CharField(max_length=255,default='',null=True)
    p_content = models.JSONField(default=dict,null=True)  
    p_directory= models.CharField(max_length=255,default='',null=True)
    p_link= models.CharField(max_length=256,default='',null=True)
    p_unique_id= models.CharField(max_length=11, db_index=True,default='',null=True,unique=True)
    def __str__(self):
        return self.p_unique_id
class Video(models.Model):
    p_unique_id = models.CharField(max_length=11, db_index=True,default='',null=True)
    v_title = models.CharField(max_length=255, default='')
    v_link= models.CharField(max_length=255, default='')
    v_pos = models.IntegerField(default=0,null=True) 
    def __str__(self):
        return self.v_title
class Keyword(models.Model):
    kw_subject= models.CharField(max_length=50, db_index=True,default='',null=True)
    kw_word = models.CharField(max_length=50,default='',null=True) 
    kw_multiple_context = models.JSONField(default=dict,null=True) 
    def __str__(self):
        return self.kw_subject + '-' + self.kw_word
class EditingTask(models.Model):
    task_subject= models.CharField(max_length=255,default='',null=True)
    task_moduel= models.CharField(max_length=255,default='',null=True)
    task_chapter= models.CharField(max_length=255,default='',null=True)
    task_topic= models.CharField(max_length=255,default='',null=True)
    task_editor = models.ForeignKey(User, on_delete=models.CASCADE,db_index=True)
    task_payment_amount = models.DecimalField(max_digits=6, decimal_places=2)
    task_completion_status= models.BooleanField(default=False,null=True)
    task_approval_status= models.BooleanField(default=False,null=True)
    def __str__(self):
        return self.task_subject +'-' + self.task_resolution

