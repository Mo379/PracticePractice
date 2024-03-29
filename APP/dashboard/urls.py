from django.urls import path, include
from . import views


# Create your views here.
app_name = 'dashboard'
urlpatterns = [
    # Superuser
    path('monitor', views.SuperuserMonitorView.as_view(), name='superuser_monitor'),
    # student
    path('student-performance/<hashid:course_id>', views.StudentPerformanceView.as_view(), name='student_performance'),
    path(
        'student-contentmanagement',
        views.StudentContentManagementView.as_view(),
        name='student_contentmanagement'
    ),
    path(
        'student-contentmanagemen/<int:page>',
        views.StudentContentManagementView.as_view,
        name='student_contentmanagement'
    ),
    # Author
    path('mycourses', views.MyCoursesView.as_view(), name='mycourses'),
    path('mycourses/<int:page>', views.MyCoursesView.as_view(), name='mycourses'),
    # extra
    path('blank', views.BlankView.as_view(), name='blank'),
    path('404', views.NotFoundView.as_view(), name='404'),
]
