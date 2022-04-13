from django.urls import path
from . import views


app_name = 'main'
urlpatterns = [
        path('', views.IndexView.as_view(), name='index'),
        path('about/',views.AboutView.as_view() , name='about'),
        path('review/', views.ReviewView.as_view(), name='review'),
        path('contact/', views.ContactView.as_view(), name='contact'),
]
