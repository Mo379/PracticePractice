from django.utils import timezone
from collections import OrderedDict
from django.db import models
from user.models import User
from mdeditor.fields import MDTextField


# Create your models here.
class Question(models.Model):
    #
    user = models.ForeignKey(
            User,
            on_delete=models.SET_NULL,
            db_index=True,
            null=True
        )
    q_in_house = models.BooleanField(default=False, null=True)
    q_level = models.CharField(max_length=30, default='', null=True)
    q_board = models.CharField(max_length=10, default='', null=True)
    q_board_moduel = models.CharField(max_length=50, default='', null=True)
    q_exam_month = models.IntegerField(default=0, null=True)
    q_exam_year = models.IntegerField(default=0, null=True)
    q_is_exam = models.BooleanField(default=False, null=True)
    q_exam_num = models.IntegerField(default=0, null=True)
    #
    q_subject = models.CharField(max_length=50, default='', null=True)
    q_moduel = models.CharField(max_length=50, default='', null=True)
    q_chapter = models.CharField(max_length=50, default='', null=True)
    q_topic = models.CharField(max_length=50, default='', null=True)
    #
    q_type = models.CharField(max_length=50, default='', null=True)
    q_difficulty = models.IntegerField(default=0, null=True)
    q_total_marks = models.IntegerField(default=0, null=True)
    q_content = models.JSONField(default=dict, null=True)
    q_dir = models.CharField(max_length=255, default='', null=True)
    q_link = models.CharField(max_length=255, default='', null=True)
    q_unique_id = models.CharField(
            max_length=11, db_index=True, default='', null=True, unique=True
        )
    deleted = models.BooleanField(default=False, null=True)

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


class Point(models.Model):
    user = models.ForeignKey(
            User,
            on_delete=models.SET_NULL,
            db_index=True,
            null=True
        )
    p_in_house = models.BooleanField(default=False, null=True)
    p_level = models.CharField(max_length=50,default='',null=True)
    p_subject = models.CharField(max_length=255,default='',null=True)
    p_moduel = models.CharField(max_length=255,default='',null=True)
    p_chapter = models.CharField(max_length=255,default='',null=True)
    p_topic = models.CharField(max_length=255,default='',null=True)
    p_number = models.IntegerField(default=-1,null=True)
    p_content = models.JSONField(default=dict,null=True)
    p_directory = models.CharField(max_length=255,default='',null=True)
    p_unique_id = models.CharField(max_length=11, db_index=True,default='',null=True,unique=True)
    deleted = models.BooleanField(default=False, null=True)

    def __str__(self):
        return self.p_unique_id


class Specification(models.Model):
    user = models.ForeignKey(
            User,
            on_delete=models.CASCADE,
            db_index=True,
            default='',
            null=True
        )
    spec_in_house = models.BooleanField(default=False, null=True)
    spec_level = models.CharField(max_length=50, default='', null=True)
    spec_subject = models.CharField(max_length=50, default='', null=True)
    spec_board = models.CharField(max_length=50, default='', null=True)
    spec_name = models.CharField(max_length=50, default='', null=True)
    spec_first_assessment = models.DateTimeField(
            'First assessment', blank=True, null=True
        )
    spec_last_assessment = models.DateTimeField(
            'Last assessment', blank=True, null=True
            )
    spec_content = models.JSONField(default=OrderedDict, null=True)
    spec_completion = models.BooleanField(default=False, null=True)
    deleted = models.BooleanField(default=False, null=True)

    def __str__(self):
        return self.spec_level + '-' + self.spec_subject + \
                '-' + self.spec_name + '-' + self.spec_board


class EditingTask(models.Model):
    specification = models.ForeignKey(
            Specification,
            on_delete=models.SET_NULL,
            db_index=True,
            null=True
        )
    task_moduel = models.CharField(max_length=255, default='', null=True)
    task_chapter = models.CharField(max_length=255, default='', null=True)
    task_topic = models.CharField(max_length=255, default='', null=True)
    task_editor = models.ForeignKey(User, on_delete=models.CASCADE, db_index=True)
    task_payment_amount = models.DecimalField(max_digits=6, decimal_places=2)
    task_completion_status = models.BooleanField(default=False, null=True)
    task_approval_status = models.BooleanField(default=False, null=True)

    def __str__(self):
        return self.specification + '-' + self.task_moduel


class Keyword(models.Model):
    specification = models.ForeignKey(
            Specification,
            on_delete=models.SET_NULL,
            db_index=True,
            null=True
        )
    kw_word = models.CharField(max_length=50, null=True)
    kw_definition = models.CharField(max_length=255, null=True)

    def __str__(self):
        return self.specification + '-' + self.kw_word


class ContentTemplate(models.Model):
    name = models.CharField(max_length=50, default='', null=True)
    content = models.JSONField(default=OrderedDict, null=True)

    def __str__(self):
        return self.name


class Course(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, db_index=True, null=True)
    specification = models.ForeignKey(
            Specification,
            on_delete=models.CASCADE,
            db_index=True,
            default='',
            null=True
        )
    course_name = models.CharField(max_length=150, default='', null=True)
    course_summary = models.TextField(max_length=1000, default='', null=True)
    course_skills = models.JSONField(default=OrderedDict, null=True)
    course_learning_objectives = models.JSONField(default=OrderedDict, null=True)
    course_contributors = models.JSONField(default=OrderedDict, null=True)
    course_language = models.CharField(max_length=150, default='', null=True)
    course_level = models.CharField(max_length=150, default='', null=True)
    course_estimated_time = models.CharField(max_length=150, default='', null=True)
    #
    course_created_at = models.DateTimeField(auto_now_add=True)
    course_updated_at = models.DateTimeField(auto_now=True)
    course_publication = models.BooleanField(default=False, null=True)
    deleted = models.BooleanField(default=False, null=True)

    def __str__(self):
        return self.course_name


class CourseVersion(models.Model):
    course = models.ForeignKey(
            Course,
            on_delete=models.CASCADE,
            db_index=True,
            default='',
            null=True
        )
    version_number = models.PositiveSmallIntegerField(null=True)
    version_name = models.CharField(max_length=150, default='', null=True)
    version_content = models.JSONField(default=OrderedDict, null=True)
    version_publication = models.BooleanField(default=False, null=True)
    version_note = models.CharField(max_length=255, default='', null=True)
    version_publication = models.BooleanField(default=False, null=True)
    version_created_at = models.DateTimeField(auto_now_add=True)
    version_updated_at = models.DateTimeField(auto_now=True)
    deleted = models.BooleanField(default=False, null=True)

    def __str__(self):
        return self.version_name


class CourseReview(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, db_index=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, db_index=True)
    review_stars = models.PositiveSmallIntegerField(null=True)
    review_text = models.CharField(max_length=255, default='', null=True)
    review_created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username + '-' + self.course.specification.spec_subject + \
                '-' + self.course.specification.spec_name


class CourseSubscription(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, db_index=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, db_index=True)

    def __str__(self):
        return self.user.username + '-' + self.course.specification.spec_subject + \
                '-' + self.course.specification.spec_name


class UserPaper(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, db_index=True)
    pap_course = models.ForeignKey(Course, on_delete=models.CASCADE, db_index=True, null=True)
    pap_info = models.JSONField(default=dict, null=True)
    pap_creation_time = models.DateTimeField('date created', auto_now_add=True, blank=True)
    deleted = models.BooleanField(default=False, null=True)

    def __str__(self):
        return self.pap_subject


class ExampleModel(models.Model):
    name = models.CharField(max_length=10)
    content = MDTextField()

    def __str__(self):
        return self.name
