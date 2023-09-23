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
        '_next_point',
        views._next_point,
        name='_next_point'
    ),
    path(
        '_ask_from_book',
        views._ask_from_book,
        name='_ask_from_book'
    ),
    path(
        '_function_app_endpoint',
        views._function_app_endpoint,
        name='_function_app_endpoint'
    ),
    path(
        '_mark_quiz_question',
        views._mark_quiz_question,
        name='_mark_quiz_question'
    ),
]

