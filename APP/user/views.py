from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.views import generic
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.core.mail import send_mail
from django.utils.functional import cached_property
from view_breadcrumbs import BaseBreadcrumbMixin
from .util.GeneralUtil import account_activation_token
from django.contrib.auth.models import User
from datetime import datetime    
from .models import *
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str 


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
        return redirect('user:login')

def _registerUser(request):
    first= request.POST['firstname']
    last= request.POST['lastname']
    username = request.POST['username']
    email = request.POST['email']
    password = request.POST['password']
    password_conf = request.POST['password_conf']
    #check if username and email are unique
    username_match = User.objects.filter(username__iexact=username).exists()
    email_match = User.objects.filter(email__iexact=email).exists()
    if password == password_conf:
        pass_safe = True
    else:
        pass_safe = False
    #return if signup is invalid
    if username_match == True or email_match == True or pass_safe==False:
        return redirect('user:register')
    # if all checks pass, proceed
    user = User.objects.create_user(
            username=username,
            email=email,
            password=password
    )
    user.first_name = first
    user.last_name = last
    user.save()
    #
    token = account_activation_token.make_token(user)
    mail_subject = 'Account activation.'
    message = render_to_string('registration/email_account_activation.html', {
        'user': user,
        'domain': '127.0.0.1:8000',
        'uid':urlsafe_base64_encode(force_bytes(user.pk)),
        'token':account_activation_token.make_token(user),
    })
    to_email = user.email
    send_mail(
        mail_subject,
        message,
        'admin@practicepractice.net',
        [to_email],
        fail_silently=False,
    )
    return redirect('user:login')
    
def _activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        try:
            u_profile = UserProfile.objects.get(user=user)
        except:
            u_profile = UserProfile.objects.create(user_id=user.id)
        u_profile.registration = 1
        u_profile.save()
        return redirect('user:login')
    else:
        return redirect('user:register')
def _logoutUser(request):
    logout(request)
    return redirect('main:index')
