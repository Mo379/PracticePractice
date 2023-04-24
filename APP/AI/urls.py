from django.urls import path, include
from AI import views


# Create your views here.
app_name = 'AI'
urlpatterns = [
    # Pages
    path('<hashid:course_id>/<module>/<chapter>/', views.AIView.as_view(), name='index'),
    path(
        '_start_new_lesson',
        views._start_new_lesson,
        name='_start_new_lesson'
    ),
    path(
        '_load_lesson',
        views._load_lesson,
        name='_load_lesson'
    ),
]

