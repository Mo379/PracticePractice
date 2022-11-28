from django.urls import path, include
from . import views


# Create your views here.
app_name = 'dashboard'
urlpatterns = [
    # general
    path('', views.IndexView.as_view(), name='index'),
    path('marketplace', views.MarketPlaceView.as_view(), name='marketplace'),
    path('marketcourse/<course_id>', views.MarketCourseView.as_view(), name='marketcourse'),
    path('coursereviews/<course_id>', views.CourseReviewsView.as_view(), name='coursereviews'),
    path('mycourses', views.MyCoursesView.as_view(), name='mycourses'),
    path(
        'specifications',
        views.MySpecificationsView.as_view(),
        name='specifications'
    ),
    path(
        'specificationoutline/<spec_id>',
        views.SpecificationOutlineView.as_view(),
        name='specificationoutline'
    ),
    path(
        'specmodule/<level>/<subject>/<board>/<name>',
        views.SpecModuelHandlerView.as_view(),
        name='specmoduel'
    ),
    path(
        'specchapter/<level>/<subject>/<board>/<name>/<module>',
        views.SpecChapterHandlerView.as_view(),
        name='specchapter'
    ),
    path(
        'spectopic/<level>/<subject>/<board>/<name>/<module>/<chapter>',
        views.SpecTopicHandlerView.as_view(),
        name='spectopic'
    ),
    path(
        'specpoint/<level>/<subject>/<board>/<name>/<module>/<chapter>/<topic>',
        views.SpecPointHandlerView.as_view(),
        name='specpoint'
    ),
    # Superuser
    path('monitor', views.SuperuserMonitorView.as_view(), name='superuser_monitor'),
    # admin
    # student
    path('student-performance', views.StudentPerformanceView.as_view(), name='student_performance'),
    path(
        'student-contentmanagement',
        views.StudentContentManagementView.as_view(),
        name='student_contentmanagement'
    ),
    # editor
    path('editor-tasks', views.EditorTasksView.as_view(), name='editor_tasks'),
    path('mytasks', views.EditorMyTasksView.as_view(), name='editor_mytasks'),
    path('editor', views.EditorEditorView.as_view(), name='editor_editor'),
    # affiliate
    path('affiliate-statistics', views.AffiliateStatisticsView.as_view(), name='affiliate_statistics'),
    # extra
    path('blank', views.BlankView.as_view(), name='blank'),
    path('404', views.NotFoundView.as_view(), name='404'),
]
