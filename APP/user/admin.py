from django.contrib import admin
from user.models import User, Admin, Student, Educator,\
        Organisation, Editor, Affiliate


# Register your models here.
admin.site.register(User)
admin.site.register(Admin)
admin.site.register(Student)
admin.site.register(Educator)
admin.site.register(Organisation)
admin.site.register(Editor)
admin.site.register(Affiliate)
