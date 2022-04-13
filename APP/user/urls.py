from django.urls import path, include
from . import views


# Create your views here.
app_name = 'user'
urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('register/', views.RegisterView.as_view(), name='register'),
    path('settings/', views.SettingsView.as_view(), name='settings'),
    path('passreset/', views.PassResetView.as_view(), name='passreset'),
    path('join/', views.JoinView.as_view(), name='join'),
     path('stripe/', include("djstripe.urls", namespace="djstripe"), name='stripe'),
    path('appearance/', views.AppearanceView.as_view(), name='appearance'),
]
