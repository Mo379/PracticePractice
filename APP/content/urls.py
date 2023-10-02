from django.urls import path
from content import views


# App name
app_name = 'content'
urlpatterns = [
    path('content/', views.ContentView.as_view(), name='content'),
    path('content/<int:page>', views.ContentView.as_view(), name='content'),
    path(
        'content/coursestudy/<hashid:course_id>/',
        views.CourseStudyView.as_view(),
        name='coursestudy'
        ),
    path(
        'content/customtest/<hashid:course_id>/<hashid:paper_id>/',
        views.CustomTestView.as_view(),
        name='customtest'
        ),
    path(
        'content/coursequiz/<hashid:course_id>/<hashid:quiz_id>/',
        views.CourseQuizView.as_view(),
        name='coursequiz'
        ),
    path(
        'content/practice/<hashid:course_id>/<module>/<chapter>/',
        views.PracticeView.as_view(),
        name='practice'
        ),
    #
    path('marketplace/', views.MarketPlaceView.as_view(), name='marketplace'),
    path('marketplace/<int:page>', views.MarketPlaceView.as_view(), name='marketplace'),
    path('marketcourse/<hashid:course_id>', views.MarketCourseView.as_view(), name='marketcourse'),
    path('coursereviews/<hashid:course_id>', views.CourseReviewsView.as_view(), name='coursereviews'),
    #
    path(
        'content/_course_subscribe/',
        views._course_subscribe,
        name='_course_subscribe'
    ),
    path(
        'content/_new_review/',
        views._new_review,
        name='_new_review'
    ),
    path(
        'content/_management_options/',
        views._management_options,
        name='_management_options'
    ),
    path(
        'content/_createcourse/',
        views._createcourse,
        name='_createcourse'
    ),
    path(
        'content/_createcustomtest/',
        views._createcustomtest,
        name='_createcustomtest'
    ),
    path(
        'content/_updatecourseinformation/',
        views._updatecourseinformation,
        name='_updatecourseinformation'
    ),
    path(
        'content/_deletecourse/',
        views._deletecourse,
        name='_deletecourse'
    ),
    path(
        'content/_subjective_mark_question/',
        views._subjective_mark_question,
        name='_subjective_mark_question'
    ),
    path(
        'content/_mark_question/',
        views._mark_question,
        name='_mark_question'
    ),
    path(
        'content/_mark_paper_question/',
        views._mark_paper_question,
        name='_mark_paper_question'
    ),
    path(
        'content/_show_answer/',
        views._show_answer,
        name='_show_answer'
    ),
]
