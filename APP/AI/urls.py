from django.urls import path, include
from AI import views


# Create your views here.
app_name = 'AI'
urlpatterns = [
    # Pages
    path('<hashid:course_id>/<module>/<chapter>/', views.AIView.as_view(), name='index'),
    path(
        '_load_lesson',
        views._load_lesson,
        name='_load_lesson'
    ),
    path(
        '_newgenerationjob',
        views._newgenerationjob,
        name='_newgenerationjob'
    ),
    path(
        '_savepromptquestion',
        views._savepromptquestion,
        name='_savepromptquestion'
    ),
    path(
        '_saveprompttopic',
        views._saveprompttopic,
        name='_saveprompttopic'
    ),
    path(
        '_savepromptpoint',
        views._savepromptpoint,
        name='_savepromptpoint'
    ),
]

