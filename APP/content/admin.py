from django.contrib import admin
from .models import Question,QuestionTrack,UserPaper, Point,Video, Keyword,EditingTask, Specification


# Register your models here.
admin.site.register(Question)
admin.site.register(QuestionTrack)
admin.site.register(UserPaper)
admin.site.register(Point)
admin.site.register(Video)
admin.site.register(Keyword)
admin.site.register(EditingTask)
admin.site.register(Specification)

