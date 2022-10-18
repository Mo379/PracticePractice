from django.db import models
from django.contrib import admin
from content.models import (
        Question,
        QuestionTrack,
        UserPaper,
        Point,
        Video,
        Keyword,
        EditingTask,
        Specification,
        SpecificationSubscription,
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
admin.site.register(Video)
admin.site.register(Keyword)
admin.site.register(EditingTask)
admin.site.register(Specification)
admin.site.register(SpecificationSubscription)
admin.site.register(ExampleModel, ExampleModelAdmin)
