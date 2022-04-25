from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.views import generic
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages

# Create your views here.
class IndexView(generic.ListView):
    template_name = "user/index.html"
    context_object_name = 'context'
    def get_queryset(self):
        return "user_index"
class LoginView(generic.ListView):
    template_name = "registration/login.html"
    context_object_name = 'context'
    def get_queryset(self):
        return "user_settings"
class RegisterView(generic.ListView):
    template_name = "registration/register.html"
    context_object_name = 'context'
    def get_queryset(self):
        return "user_settings"
class ForgotPasswordView(generic.ListView):
    template_name = "registration/forgot-password.html"
    context_object_name = 'context'
    def get_queryset(self):
        return "user_settings"
class SettingsView(generic.ListView):
    template_name = "user/settings.html"
    context_object_name = 'context'
    def get_queryset(self):
        return "user_settings"
class JoinView(generic.ListView):
    template_name = "user/join.html"
    context_object_name = 'context'
    def get_queryset(self):
        return "user_join"
class CheckoutStripeView(generic.ListView):
    template_name = "user/checkout-stripe.html"
    context_object_name = 'context'
    def get_queryset(self):
        return "user_checkout-strip"
class CheckoutPaypalView(generic.ListView):
    template_name = "user/checkout-paypal.html"
    context_object_name = 'context'
    def get_queryset(self):
        return "user_checkout-stripe"
class AppearanceView(generic.ListView):
    template_name = "user/action.html"
    context_object_name = 'context'
    def get_queryset(self):
        return "user_appearance_action"

















# Authentication system
def _loginUser(request):
    username = request.POST['username']
    password = request.POST['password']
    user = authenticate(request, username=username, password=password)
    if user is not None:
        login(request, user)
        # Redirect to a success page.
        return redirect('user:index')
    else:
        # Return an 'invalid login' error message.
        return redirect('user:settings')
def _logoutUser(request):
    logout(request)
    return redirect('main:index')
