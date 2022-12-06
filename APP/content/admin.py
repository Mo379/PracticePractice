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
        Course,
        CourseVersion,
        CourseReview,
        CourseSubscription,
        )


# Register your models here.
admin.site.register(Question)
admin.site.register(QuestionTrack)
admin.site.register(UserPaper)
admin.site.register(Point)
admin.site.register(Keyword)
admin.site.register(EditingTask)
admin.site.register(Specification)
admin.site.register(Course)
admin.site.register(CourseVersion)
admin.site.register(CourseReview)
admin.site.register(CourseSubscription)
