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
    moduel = models.CharField(max_length=50, default="", null=True)
    lesson_chat = models.JSONField(default=dict, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    terminated_at = models.DateTimeField(null=True, default=None, blank=True)

    def __str__(self):
        return self.user.username + self.course + self.moduel
