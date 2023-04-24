from django.urls import path, include
from . import views


# Create your views here.
app_name = 'dashboard'
urlpatterns = [
    # Superuser
    path('monitor', views.SuperuserMonitorView.as_view(), name='superuser_monitor'),
    # general
    path('', views.IndexView.as_view(), name='index'),
    path('marketplace/', views.MarketPlaceView.as_view(), name='marketplace'),
    path('marketplace/<int:page>', views.MarketPlaceView.as_view(), name='marketplace'),
    path('marketcourse/<hashid:course_id>', views.MarketCourseView.as_view(), name='marketcourse'),
    path('coursereviews/<hashid:course_id>', views.CourseReviewsView.as_view(), name='coursereviews'),
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
    # Author
    path('mycourses', views.MyCoursesView.as_view(), name='mycourses'),
    path('mycourses/<int:page>', views.MyCoursesView.as_view(), name='mycourses'),
    path(
        'specifications',
        views.MySpecificationsView.as_view(),
        name='specifications'
    ),
    path(
        'specmodule/<level>/<subject>/<board>/<name>',
        views.SpecModuelHandlerView.as_view(),
        name='specmoduel'
    ),
    path(
        'spectopic/<level>/<subject>/<board>/<name>/<module>/<chapter>',
        views.SpecTopicHandlerView.as_view(),
        name='spectopic'
    ),
    path('earning-statistics', views.EarningStatisticsView.as_view(), name='earning_statistics'),
    # extra
    path('blank', views.BlankView.as_view(), name='blank'),
    path('404', views.NotFoundView.as_view(), name='404'),
]
