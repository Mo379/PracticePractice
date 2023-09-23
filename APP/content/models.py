from django.utils import timezone
from collections import OrderedDict
from django.db import models
from user.models import User

from django.db import models


class Image(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, db_index=True, null=True)
    description = models.TextField(max_length=1000, default="", null=True)
    url = models.TextField(max_length=1000, default="", null=True)
    in_question_placement = models.BooleanField(default=False, null=True)

    def __str__(self):
        return self.url


class Video(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, db_index=True, null=True)
    title = models.CharField(max_length=255, default="", null=True)
    transcript = models.JSONField(default=dict, null=True)
    url = models.TextField(max_length=1000, default="", null=True)
    in_question_placement = models.BooleanField(default=False, null=True)

    def __str__(self):
        return self.title


# Create your models here.
class Question(models.Model):
    #
    user = models.ForeignKey(User, on_delete=models.SET_NULL, db_index=True, null=True)
    #
    q_subject = models.CharField(max_length=50, default="", null=True)
    q_moduel = models.CharField(max_length=50, default="", null=True)
    q_chapter = models.CharField(max_length=50, default="", null=True)
    q_number = models.IntegerField(default=0, null=True)
    #
    q_difficulty = models.IntegerField(default=0, null=True)
    q_marks = models.IntegerField(default=1)
    q_content = models.JSONField(default=dict, null=True)
    q_answer = models.JSONField(default=dict, null=True)
    q_files_directory = models.CharField(max_length=255, default="", null=True)
    q_videos = models.ManyToManyField(Video)
    q_images = models.ManyToManyField(Image)
    q_unique_id = models.CharField(
        max_length=11, db_index=True, default="", null=True, unique=True
    )
    author_confirmation = models.BooleanField(default=False, null=True)
    deleted = models.BooleanField(default=False, null=True)
    erased = models.BooleanField(default=False, null=True)

    def __str__(self):
        return self.q_unique_id


class Point(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, db_index=True, null=True)
    p_in_house = models.BooleanField(default=False, null=True)
    p_level = models.CharField(max_length=50, default="", null=True)
    p_subject = models.CharField(max_length=255, default="", null=True)
    p_moduel = models.CharField(max_length=255, default="", null=True)
    p_chapter = models.CharField(max_length=255, default="", null=True)
    p_topic = models.CharField(max_length=255, default="", null=True)
    p_title = models.CharField(max_length=255, default="", null=True)
    p_number = models.IntegerField(default=-1, null=True)
    p_content = models.JSONField(default=dict, null=True)
    p_files_directory = models.CharField(max_length=255, default="", null=True)
    p_images = models.ManyToManyField(Image)
    p_videos = models.ManyToManyField(Video)
    p_unique_id = models.CharField(
        max_length=11, db_index=True, default="", null=True, unique=True
    )
    is_completed_content = models.BooleanField(default=False, null=True)
    is_completed_questions = models.BooleanField(default=False, null=True)
    author_confirmation = models.BooleanField(default=False, null=True)
    deleted = models.BooleanField(default=False, null=True)
    erased = models.BooleanField(default=False, null=True)

    def __str__(self):
        return self.p_unique_id


class Specification(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, db_index=True, default="", null=True
    )
    spec_in_house = models.BooleanField(default=False, null=True)
    spec_level = models.CharField(max_length=50, default="", null=True)
    spec_subject = models.CharField(max_length=50, default="", null=True)
    spec_board = models.CharField(max_length=50, default="", null=True)
    spec_name = models.CharField(max_length=50, default="", null=True)
    spec_first_assessment = models.DateTimeField(
        "First assessment", blank=True, null=True
    )
    spec_last_assessment = models.DateTimeField(
        "Last assessment", blank=True, null=True
    )
    spec_content = models.JSONField(default=OrderedDict, null=True)
    deleted = models.BooleanField(default=False, null=True)

    def __str__(self):
        return (
            self.spec_level
            + "-"
            + self.spec_subject
            + "-"
            + self.spec_name
            + "-"
            + self.spec_board
        )


class ContentTemplate(models.Model):
    name = models.CharField(max_length=50, default="", null=True)
    content = models.JSONField(default=OrderedDict, null=True)

    def __str__(self):
        return self.name


class Course(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, db_index=True, null=True)
    specification = models.ForeignKey(
        Specification, on_delete=models.CASCADE, db_index=True, default="", null=True
    )
    course_name = models.CharField(max_length=150, default="", null=True)
    course_summary = models.TextField(max_length=1000, default="", null=True)
    course_skills = models.JSONField(default=OrderedDict, null=True)
    course_learning_objectives = models.JSONField(default=OrderedDict, null=True)
    course_level = models.CharField(max_length=150, default="", null=True)
    #
    course_created_at = models.DateTimeField(auto_now_add=True)
    course_updated_at = models.DateTimeField(auto_now=True)
    course_up_to_date = models.BooleanField(default=False, null=True)
    course_publication = models.BooleanField(default=False, null=True)
    course_pic_ext = models.CharField(max_length=150, default="", null=True)
    course_pic_status = models.BooleanField(default=False)
    deleted = models.BooleanField(default=False, null=True)

    def __str__(self):
        return self.course_name

class CourseVersion(models.Model):
    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, db_index=True, default="", null=True
    )
    version_number = models.PositiveSmallIntegerField(null=True)
    version_name = models.CharField(max_length=150, default="", null=True)
    version_content = models.JSONField(default=OrderedDict, null=True)
    version_publication = models.BooleanField(default=False, null=True)
    version_note = models.CharField(max_length=255, default="", null=True)
    version_publication = models.BooleanField(default=False, null=True)
    version_created_at = models.DateTimeField(auto_now_add=True)
    version_updated_at = models.DateTimeField(auto_now=True)
    deleted = models.BooleanField(default=False, null=True)

    def __str__(self):
        return self.version_name


class CourseSubscription(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, db_index=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, db_index=True)
    visibility = models.BooleanField(default=True, null=True)
    owned = models.BooleanField(default=False, null=True)
    subscription_created_at = models.DateTimeField(auto_now_add=True)
    subscription_ended_at = models.DateTimeField(null=True, default=None, blank=True)
    monthly_significant_clicks = models.JSONField(default=OrderedDict, null=True)
    progress_track = models.JSONField(default=dict, null=True)

    def __str__(self):
        return (
            self.user.username
            + "-"
            + self.course.specification.spec_subject
            + "-"
            + self.course.specification.spec_name
        )


class CourseReview(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, db_index=True, null=True)
    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, db_index=True, default="", null=True
    )
    rating = models.PositiveSmallIntegerField(null=True)
    review = models.TextField(max_length=2500, default="", null=True)
    review_created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.user.username) + str(self.course)

class QuestionTrack(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, db_index=True)
    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, db_column="specification", db_index=True
    )
    question = models.ForeignKey(
        Question, on_delete=models.CASCADE, db_column="q_unique_id", db_index=True
    )
    CHOICES_Marks = [
        ('1', 'Easy'),
        ('2', 'Ok'),
        ('3', 'Hard'),
    ]
    precieved_difficulty = models.CharField(
        max_length=1,
        choices=CHOICES_Marks,
        null=True
    )
    track_mark = models.IntegerField(default=0, null=True)
    total_marks = models.IntegerField(default=0, null=True)
    track_attempt_number = models.IntegerField(default=0, null=True)
    track_creation_time = models.DateTimeField(
        "date created", auto_now_add=True, blank=True
    )

    def __str__(self):
        return self.user.username + '-' + str(self.question.id)


class UserPaper(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, db_index=True)
    pap_course = models.ForeignKey(
        Course, on_delete=models.CASCADE, db_index=True, null=True
    )
    pap_info = models.JSONField(default=dict, null=True)
    pap_creation_time = models.DateTimeField(
        "date created", auto_now_add=True, blank=True
    )
    pap_q_marks = models.JSONField(default=dict, null=True)
    pap_completion = models.BooleanField(default=False, null=True)
    percentage_score = models.DecimalField(
        default=0.0,
        max_digits=5,  # Maximum number of digits allowed (including decimals).
        decimal_places=1,  # Number of decimal places.
    )
    deleted = models.BooleanField(default=False, null=True)

    def __str__(self):
        return self.user.username
