from django.urls import path
from content import views


# App name
app_name = 'content'
urlpatterns = [
    path('content', views.ContentView.as_view(), name='content'),
    path('content/questions', views.QuestionsView.as_view(), name='questions'),
    path(
        'content/question/<level>/<subject>/<board>/<specification>/<module>/<chapter>/',
        views.QuestionView.as_view(),
        name='question'
        ),
    path('content/notes', views.NotesView.as_view(), name='notes'),
    path(
        'content/note-article/<level>/<subject>/<board>/<specification>/<module>/<chapter>/',
        views.NoteArticleView.as_view(),
        name='notearticle'
    ),
    path('content/papers', views.PapersView.as_view(), name='papers'),
    path('content/paper/<subject>/<board>/<board_moduel>/<exam_year>/<exam_month>/', views.PaperView.as_view(), name='paper'),
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
        'content/_syncspecifications',
        views._syncspecifications,
        name='_syncspecifications'
    ),
    path(
        'content/_syncspecquestions',
        views._syncspecquestions,
        name='_syncspecquestions'
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
    path(
        'content/_inheritfromspec',
        views._inheritfromspec,
        name='_inheritfromspec'
    ),
    path(
        'content/_ordermoduels',
        views._ordermoduels,
        name='_ordermoduels'
    ),
    path(
        'content/_orderchapters',
        views._orderchapters,
        name='_orderchapters'
    ),
    path(
        'content/_ordertopics',
        views._ordertopics,
        name='_ordertopics'
    ),
    path(
        'content/_orderpoints',
        views._orderpoints,
        name='_orderpoints'
    ),
    path(
        'content/_specificationsubscription/<level>/<subject>/<board>/<name>',
        views._specificationsubscription,
        name='_specificationsubscription'
    ),
]
