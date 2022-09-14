from django.urls import path, include
from . import views


# Create your views here.
app_name = 'dashboard'
urlpatterns = [
    # general
    path('', views.IndexView.as_view(), name='index'),
    # admin
    path('traffic', views.AdminTrafficView.as_view(), name='admin_traffic'),
    # student
    path('student-performance', views.StudentPerformanceView.as_view(), name='student_performance'),
    # teacher
    path('teacher-classes', views.TeacherClassesView.as_view(), name='teacher_classes'),
    # private tutor
    path('tutor-classes', views.TutorClassesView.as_view(), name='tutor_classes'),
    # school
    path('school-management', views.SchoolManagementView.as_view(), name='school_management'),
    # tuition center
    path('center-management', views.CenterManagementView.as_view(), name='center_management'),
    # editor
    path('editor-tasks', views.EditorTasksView.as_view(), name='editor_tasks'),
    # affiliate
    path('affiliate-statistics', views.AffiliateStatisticsView.as_view(), name='affiliate_statistics'),
    # extra
    path('blank', views.BlankView.as_view(), name='blank'),
    path('404', views.NotFoundView.as_view(), name='404'),
]
