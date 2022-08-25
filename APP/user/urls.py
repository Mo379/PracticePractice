from django.urls import path, include
from user import views


# Create your views here.
app_name = 'user'
urlpatterns = [
    # Pages
    path('', views.IndexView.as_view(), name='index'),
    path('login', views.LoginView.as_view(), name='login'),
    path('register', views.RegisterView.as_view(), name='register'),
    path(
        'forgotpassword',
        views.ForgotPasswordView.as_view(),
        name='forgot-password'
    ),
    path(
        'pwdreset/<uidb64>/<token>',
        views.PwdResetView.as_view(),
        name='pwdreset'
    ),
    path('billing', views.BillingView.as_view(), name='billing'),
    path('security', views.SecurityView.as_view(), name='security'),
    path('settings', views.SettingsView.as_view(), name='settings'),
    path('join', views.JoinView.as_view(), name='join'),
    # actions
    path('_login', views._loginUser, name='_login'),
    path('_registerUser', views._registerUser, name='_register'),
    path('_pwdreset_form', views._pwdreset_form, name='_pwdreset_form'),
    path('_pwdreset', views._pwdreset, name='_pwdreset'),
    path('_activate/<uidb64>/<token>', views._activate, name='_activate'),
    path('_logout', views._logoutUser, name='_logout'),
    path('_appearance', views._logoutUser, name='_appearance'),
]
