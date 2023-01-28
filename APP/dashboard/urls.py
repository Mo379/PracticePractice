from django.urls import path, include
from . import views


# Create your views here.
app_name = 'dashboard'
urlpatterns = [
    # general
    path('', views.IndexView.as_view(), name='index'),
    path('marketplace/', views.MarketPlaceView.as_view(), name='marketplace'),
    path('marketplace/<int:page>', views.MarketPlaceView.as_view(), name='marketplace'),
    path('marketcourse/<hashid:course_id>', views.MarketCourseView.as_view(), name='marketcourse'),
    path('coursereviews/<hashid:course_id>', views.CourseReviewsView.as_view(), name='coursereviews'),
    path('mycourses', views.MyCoursesView.as_view(), name='mycourses'),
    path('mycourses/<int:page>', views.MyCoursesView.as_view(), name='mycourses'),
    path(
        'specifications',
        views.MySpecificationsView.as_view(),
        name='specifications'
    ),
    path(
        'specificationoutline/<hashid:spec_id>',
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
    # collaborator
    path('contribute', views.CollabContributeView.as_view(), name='collab_contribute'),
    path('manage-collaborations', views.CollabManageView.as_view(), name='collab_manage'),
    path('review-work', views.CollabReviewView.as_view(), name='collab_review'),
    path('manage-collaborators', views.CollaboratorsManageView.as_view(), name='collaborators_manage'),
    # student
    path('student-performance', views.StudentPerformanceView.as_view(), name='student_performance'),
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
    # affiliate
    path('earning-statistics', views.EarningStatisticsView.as_view(), name='earning_statistics'),
    # extra
    path('blank', views.BlankView.as_view(), name='blank'),
    path('404', views.NotFoundView.as_view(), name='404'),
]
