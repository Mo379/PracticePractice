from django.contrib import admin
from user.models import User, Admin, Student, Teacher, PrivateTutor, \
        School, TuitionCenter, Editor, Affiliate


# Register your models here.
admin.site.register(User)
admin.site.register(Admin)
admin.site.register(Student)
admin.site.register(Teacher)
admin.site.register(PrivateTutor)
admin.site.register(School)
admin.site.register(TuitionCenter)
admin.site.register(Editor)
admin.site.register(Affiliate)
