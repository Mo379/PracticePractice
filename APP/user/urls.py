from django.urls import path, include
from . import views


# Create your views here.
app_name = 'user'
urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    # Login system
    path('login', views.LoginUser, name='login'),
    path('logout', views.LogoutUser, name='logout'),
    #
    path('settings/', views.SettingsView.as_view(), name='settings'),
    path('join/', views.JoinView.as_view(), name='join'),
    path('join/checkout/stripe', views.CheckoutStripeView.as_view(), name='checkout-stripe'),
    path('join/checkout/paypal', views.CheckoutPaypalView.as_view(), name='checkout-paypal'),
    path('stripe/', include("djstripe.urls", namespace="djstripe"), name='stripe'),
    path('appearance/', views.AppearanceView.as_view(), name='appearance'),
]
