from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
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
def login_user(request):
    pass



