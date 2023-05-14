from django.db import models
from django.contrib import admin
from content.models import (
        Image,
        Video,
        Question,
        QuestionTrack,
        UserPaper,
        Point,
        Keyword,
        Specification,
        Collaborator,
        ContributionTask,
        Contribution,
        Contract,
        ContentTemplate,
        Course,
        CourseVersion,
        CourseReview,
        CourseSubscription,
        )


# Register your models here.
admin.site.register(Image)
admin.site.register(Video)
admin.site.register(Question)
admin.site.register(QuestionTrack)
admin.site.register(UserPaper)
admin.site.register(Point)
admin.site.register(Keyword)
admin.site.register(Specification)
admin.site.register(Collaborator)
admin.site.register(ContributionTask)
admin.site.register(Contribution)
admin.site.register(Contract)
admin.site.register(ContentTemplate)
admin.site.register(Course)
admin.site.register(CourseVersion)
admin.site.register(CourseReview)
admin.site.register(CourseSubscription)
