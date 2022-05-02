from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.views import generic
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.utils.functional import cached_property
from view_breadcrumbs import BaseBreadcrumbMixin

# Create your views here.






class IndexView(BaseBreadcrumbMixin, generic.ListView):
    template_name = "user/index.html"
    context_object_name = 'context'
    @cached_property
    def crumbs(self):
        return [
                ("account", reverse("user:index")),
                ("profile", reverse("user:index"))
                ]
    def get_queryset(self):
        return "user_index"












class LoginView(BaseBreadcrumbMixin, generic.ListView):
    template_name = "registration/login.html"
    context_object_name = 'context'
    @cached_property
    def crumbs(self):
        return [
                ("login", reverse("user:login"))
                ]
    def get_queryset(self):
        return "user_settings"








class RegisterView(BaseBreadcrumbMixin, generic.ListView):
    template_name = "registration/register.html"
    context_object_name = 'context'
    @cached_property
    def crumbs(self):
        return [
                ("register", reverse("user:register"))
                ]
    def get_queryset(self):
        return "user_settings"








class ForgotPasswordView(BaseBreadcrumbMixin, generic.ListView):
    template_name = "registration/forgot-password.html"
    context_object_name = 'context'
    @cached_property
    def crumbs(self):
        return [
                ("forgot-password", reverse("user:forgot-password"))
                ]
    def get_queryset(self):
        return "user_settings"








class BillingView(BaseBreadcrumbMixin, generic.ListView):
    template_name = "user/billing.html"
    context_object_name = 'context'
    @cached_property
    def crumbs(self):
        return [
                ("account", reverse("user:index")),
                ("billing", reverse("user:billing"))
                ]
    def get_queryset(self):
        return "user_settings"








class SecurityView(BaseBreadcrumbMixin, generic.ListView):
    template_name = "user/security.html"
    context_object_name = 'context'
    @cached_property
    def crumbs(self):
        return [
                ("account", reverse("user:index")),
                ("security", reverse("user:security")),
                ]
    def get_queryset(self):
        return "user_settings"








class SettingsView(BaseBreadcrumbMixin, generic.ListView):
    template_name = "user/settings.html"
    context_object_name = 'context'
    @cached_property
    def crumbs(self):
        return [
                ("account", reverse("user:index")),
                ("settings", reverse("user:settings")),
                ]
    def get_queryset(self):
        return "user_settings"








class JoinView(BaseBreadcrumbMixin, generic.ListView):
    template_name = "user/join.html"
    context_object_name = 'context'
    @cached_property
    def crumbs(self):
        return [
                ("account", reverse("user:index")),
                ("join", reverse("user:join")),
                ]
    def get_queryset(self):
        return "user_join"








class CheckoutStripeView(BaseBreadcrumbMixin, generic.ListView):
    template_name = "user/checkout-stripe.html"
    context_object_name = 'context'
    @cached_property
    def crumbs(self):
        return [
                ("account", reverse("user:index")),
                ("join", reverse("user:join")),
                ("checkout", ''),
                ("stripe", reverse("user:checkout-stripe")),
                ]
    def get_queryset(self):
        return "user_checkout-strip"








class CheckoutPaypalView(BaseBreadcrumbMixin, generic.ListView):
    template_name = "user/checkout-paypal.html"
    context_object_name = 'context'
    @cached_property
    def crumbs(self):
        return [
                ("account", reverse("user:index")),
                ("join", reverse("user:join")),
                ("checkout", ''),
                ("paypal", reverse("user:checkout-paypal")),
                ]
    def get_queryset(self):
        return "user_checkout-stripe"








class AppearanceView(BaseBreadcrumbMixin, generic.ListView):
    template_name = "user/action.html"
    context_object_name = 'context'
    @cached_property
    def crumbs(self):
        return [
                ("account", reverse("user:index")),
                ("settings", reverse("user:settings")),
                ("apperance", reverse("user:apperance")),
                ]
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
