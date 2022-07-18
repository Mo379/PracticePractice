from django.urls import path, include
from . import views


# Create your views here.
app_name = 'user'
urlpatterns = [
    # Pages
    path('', views.IndexView.as_view(), name='index'),
    path('login', views.LoginView.as_view(), name='login'),
    path('register', views.RegisterView.as_view(), name='register'),
    path('forgotpassword', views.ForgotPasswordView.as_view(), name='forgot-password'),
    path('billing', views.BillingView.as_view(), name='billing'),
    path('security', views.SecurityView.as_view(), name='security'),
    path('settings', views.SettingsView.as_view(), name='settings'),
    path('join', views.JoinView.as_view(), name='join'),
    #actions
    path('_login', views._loginUser, name='_login'),
    path('_registerUser', views._registerUser, name='_register'),
    path('_activate/<uidb64>/<token>', views._activate, name='_activate'),
    path('_logout', views._logoutUser, name='_logout'),
    path('_appearance', views._logoutUser, name='_appearance'),
]
