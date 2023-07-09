from django.db import models
from user.models import User
from content.models import Specification, Course


# Prompt Usage
class Usage(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, db_index=True, default="", null=False,
        related_name='AI_usage_user'
    )
    model = models.CharField(max_length=150, default="", null=True)
    prompt = models.IntegerField(default=0, null=True)
    completion = models.IntegerField(default=0, null=True)
    total = models.IntegerField(default=0, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.user.username) + str(self.created_at)


class ContentGenerationJob(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, db_index=True, default="", null=False,
        related_name='AI_contentgeneration_user'
    )
    specification = models.ForeignKey(
        Specification, on_delete=models.CASCADE, db_index=True, default="", null=False,
        related_name='AI_contentjob'
    )
    moduel = models.CharField(max_length=255, default="", null=True)
    chapter = models.CharField(max_length=255, default="", null=True)
    #
    model = models.CharField(max_length=150, default="", null=True)
    prompt = models.IntegerField(default=0, null=True)
    completion = models.IntegerField(default=0, null=True)
    total = models.IntegerField(default=0, null=True)
    finished = models.BooleanField(default=False, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.user.username) + str(self.created_at)


class ContentPromptQuestion(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, db_index=True, default="", null=False,
        related_name='AI_contentprompt_user_question'
    )
    specification = models.ForeignKey(
        Specification, on_delete=models.CASCADE, db_index=True, default="", null=False,
        related_name='AI_contentprompt_specification_question'
    )
    moduel = models.CharField(max_length=255, default="", null=True)
    chapter = models.CharField(max_length=255, default="", null=True)
    level = models.IntegerField(default=-1, null=True)
    prompt = models.TextField(max_length=2500, default="", null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    activated = models.BooleanField(default=False, null=True)

    def __str__(self):
        return str(self.user) + str(self.specification)


class ContentPromptTopic(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, db_index=True, default="", null=False,
        related_name='AI_contentprompt_user_topic'
    )
    specification = models.ForeignKey(
        Specification, on_delete=models.CASCADE, db_index=True, default="", null=False,
        related_name='AI_contentprompt_specification_topic'
    )
    moduel = models.CharField(max_length=255, default="", null=True)
    chapter = models.CharField(max_length=255, default="", null=True)
    topic = models.CharField(max_length=255, default="", null=True)
    prompt = models.TextField(max_length=2500, default="", null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.user) + str(self.specification)


class ContentPromptPoint(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, db_index=True, default="", null=False,
        related_name='AI_contentprompt_user_point'
    )
    specification = models.ForeignKey(
        Specification, on_delete=models.CASCADE, db_index=True, default="", null=False,
        related_name='AI_contentprompt_specification_point'
    )
    moduel = models.CharField(max_length=255, default="", null=True)
    chapter = models.CharField(max_length=255, default="", null=True)
    topic = models.CharField(max_length=255, default="", null=True)
    p_unique = models.CharField(
        max_length=11, default="", null=True
    )
    prompt = models.TextField(max_length=2500, default="", null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    activated = models.BooleanField(default=False, null=True)

    def __str__(self):
        return str(self.user) + str(self.specification)


# Create your models here.
class Lesson(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, db_index=True, default="", null=False,
        related_name='AI_lesson_user'
    )
    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, db_index=True,
        default="", null=False, related_name='AI_lesson_course'
    )
    moduel = models.CharField(max_length=150, default="", null=True)
    chapter = models.CharField(max_length=150, default="", null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username + self.course.course_name + self.moduel


class Lesson_part(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, db_index=True, default="", null=False,
        related_name='AI_lesson_part_user'
    )
    lesson = models.ForeignKey(
        Lesson, on_delete=models.CASCADE, db_index=True,
        default="", null=False, related_name='AI_lesson_course'
    )
    topic = models.CharField(max_length=150, default="", null=True)
    part_content = models.JSONField(default=dict, null=True)
    part_chat = models.JSONField(default=dict, null=True)
    prompt = models.IntegerField(default=0, null=True)
    completion = models.IntegerField(default=0, null=True)
    total = models.IntegerField(default=0, null=True)
    recording_switch = models.BooleanField(default=False, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    terminated_at = models.DateTimeField(null=True, default=None, blank=True)

    def __str__(self):
        return self.user.username + '-' + self.topic
