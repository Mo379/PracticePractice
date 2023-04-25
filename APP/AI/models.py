from django.db import models
from user.models import User
from content.models import Course


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
    lesson_content = models.JSONField(default=dict, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    terminated_at = models.DateTimeField(null=True, default=None, blank=True)

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
    part_introduction = models.TextField(default='', null=True)
    part_content = models.JSONField(default=dict, null=True)
    part_chat = models.JSONField(default=dict, null=True)
    part_pointer = models.CharField(max_length=250, default="", null=True)
    part_token_count = models.IntegerField(default=0, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    terminated_at = models.DateTimeField(null=True, default=None, blank=True)

    def __str__(self):
        return self.user.username + '-' + self.lesson.moduel + '-' + self.chapter
