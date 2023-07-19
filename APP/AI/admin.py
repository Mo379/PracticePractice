from django.db import models
from django.contrib import admin
from AI.models import (
        Usage,
        ContentGenerationJob,
        ContentPromptQuestion,
        ContentPromptTopic,
        ContentPromptPoint,
        Lesson,
        Lesson_part,
        Lesson_quiz,
    )

admin.site.register(Usage)
admin.site.register(ContentGenerationJob)
admin.site.register(ContentPromptQuestion)
admin.site.register(ContentPromptTopic)
admin.site.register(ContentPromptPoint)
admin.site.register(Lesson)
admin.site.register(Lesson_part)
admin.site.register(Lesson_quiz)
# Register your models here.
