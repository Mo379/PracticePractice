from django.db import models
from django.contrib import admin
from AI.models import (
        Usage,
        Lesson,
        Lesson_part,
    )

admin.site.register(Usage)
admin.site.register(Lesson)
admin.site.register(Lesson_part)
# Register your models here.
