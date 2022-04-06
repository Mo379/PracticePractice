from django.contrib import admin
from .models import Question,QuestionTrack,Point,Video,UserPaper


# Register your models here.
admin.site.register(Question)
admin.site.register(QuestionTrack)
admin.site.register(Point)
admin.site.register(Video)
admin.site.register(UserPaper)

