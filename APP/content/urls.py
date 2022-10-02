from django.urls import path
from content import views


# App name
app_name = 'content'
urlpatterns = [
    path('content', views.ContentView.as_view(), name='content'),
    path('content/questions', views.QuestionsView.as_view(), name='questions'),
    path(
        'content/question/<level>/<subject>/<specification>/<module>/<chapter>/<page>/',
        views.QuestionView.as_view(),
        name='question'
        ),
    path('content/notes', views.NotesView.as_view(), name='notes'),
    path(
        'content/note-article/<level>/<subject>/<specification>/<module>/<chapter>/',
        views.NoteArticleView.as_view(),
        name='notearticle'
    ),
    path('content/paper', views.PaperView.as_view(), name='paper'),
    #
    path('content/_media', views._media, name='_media'),
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
