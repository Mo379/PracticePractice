from django.urls import path
from . import views


app_name = 'main'
urlpatterns = [
        path('', views.IndexView.as_view(), name='index'),
        path('about/',views.AboutView.as_view() , name='about'),
        path('review/', views.ReviewView.as_view(), name='review'),
        path('contact/', views.ContactView.as_view(), name='contact'),
        path('jobs/', views.JobsView.as_view(), name='jobs'),
        path('faq/', views.FAQView.as_view(), name='faq'),
        path('tandc/', views.TermsAndConditionsView.as_view(), name='tandc'),
        path('privacy/', views.PrivacyView.as_view(), name='privacy'),
        path('sitemap/', views.SiteMapView.as_view(), name='sitemap'),
        path('sitemapseo/', views.SiteMapSEOView.as_view(), name='sitemapseo'),
]
