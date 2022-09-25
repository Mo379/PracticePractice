from django.urls import path
from content import views


# App name
app_name = 'content'
urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('hub', views.HubView.as_view(), name='hub'),
    path('statistics', views.StatisticsView.as_view(), name='statistics'),
    path('content', views.ContentView.as_view() , name='content'),
    path('content/questions', views.QuestionsView.as_view(), name='questions'),
    path('content/question', views.QuestionView.as_view(), name='question'),
    path('content/notes', views.NotesView.as_view(), name='notes'),
    path('content/paper', views.PaperView.as_view(), name='paper'),
    path('content/user-paper', views.UserPaperView.as_view(), name='user-paper'),
    path('content/user-paper/print', views.UserPaperPrintView.as_view(), name='user-paper-print'),
    #
    path(
        'content/_syncnotes',
        views._syncnotes,
        name='_syncnotes'
    ),
    path(
        'content/_syncquestions',
        views._syncquestions,
        name='_syncquestions'
    ),
    path(
        'content/_syncvideos',
        views._syncvideos,
        name='_syncvideos'
    ),
    path(
        'content/_checkvideohealth',
        views._checkvideohealth,
        name='_checkvideohealth'
    ),
]
