from django.urls import path, include
from AI import views


# Create your views here.
app_name = 'AI'
urlpatterns = [
    # Pages
    path('', views.AIView.as_view(), name='index'),
]

