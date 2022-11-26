from django.db import models
from django.contrib import admin
from content.models import (
        Question,
        QuestionTrack,
        UserPaper,
        Point,
        Keyword,
        EditingTask,
        Specification,
        ContentTemplate,
        Course,
        CourseVersion,
        CourseReview,
        CourseSubscription,
        ExampleModel
        )

# Register your models here.
from mdeditor.widgets import MDEditorWidget


class ExampleModelAdmin (admin.ModelAdmin):
    formfield_overrides = {
        models.TextField: {'widget': MDEditorWidget}
    }


# Register your models here.
admin.site.register(Question)
admin.site.register(QuestionTrack)
admin.site.register(UserPaper)
admin.site.register(Point)
admin.site.register(Keyword)
admin.site.register(EditingTask)
admin.site.register(Specification)
admin.site.register(ContentTemplate)
admin.site.register(Course)
admin.site.register(CourseVersion)
admin.site.register(CourseReview)
admin.site.register(CourseSubscription)
admin.site.register(ExampleModel, ExampleModelAdmin)
