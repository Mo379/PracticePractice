from django.urls import path
from . import views


app_name = 'content'
urlpatterns = [
        path('', views.IndexView.as_view(), name='index'),
        path('hub', views.HubView.as_view(), name='hub'),
]
