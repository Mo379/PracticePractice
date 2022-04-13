from django.urls import path
from . import views


app_name = 'content'
urlpatterns = [
        path('', views.IndexView.as_view(), name='index'),
        path('content/',views.ContentView.as_view() , name='content'),
        path('hub/', views.HubView.as_view(), name='hub'),
        path('statistics/', views.StatisticsView.as_view(), name='statistics'),
]
