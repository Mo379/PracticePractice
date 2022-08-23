from django.conf import settings
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
from django.contrib.auth.models import User, Group
from datetime import datetime   
from .models import UserProfile
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


# Login view
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


# Register View
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


# Forgot password view
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


# Billing view
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


# Secutiry view
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


# Settings view
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


# Join view
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


# Appearance View
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
# user login action
def _loginUser(request):
    username = request.POST['username']
    password = request.POST['password']
    auth = authenticate(request, username=username, password=password)
    user = User.objects.get(username__iexact=username)
    try:
        registration = UserProfile.objects.get(user=user).registration
    except Exception:
        registration = False
        if user.is_superuser is None:
            messages.add_message(
                    request,
                    messages.INFO,
                    'Registration is required before a login is allowed.',
                    extra_tags='alert-danger login_form'
                )
    if auth is None:
        messages.add_message(
                request,
                messages.INFO,
                'Incorrect details, plese try again or create an account.',
                extra_tags='alert-danger login_form'
            )
    if auth is not None and (registration == True or user.is_superuser):
        login(request, user)
        messages.add_message(
                request,
                messages.INFO,
                'Successfull login!',
                extra_tags='alert-success user_profile'
            )
        # Redirect to a success page.
        return redirect('user:index')
    else:
        # Return an 'invalid login' error message.
        return redirect('user:login')


# Register user action
def _registerUser(request):
    utype = request.POST['usertype']
    first = request.POST['firstname']
    last = request.POST['lastname']
    username = request.POST['username']
    email = request.POST['email']
    password = request.POST['password']
    password_conf = request.POST['password_conf']
    # check if username and email are unique
    username_match = User.objects.filter(username__iexact=username).exists()
    email_match = User.objects.filter(email__iexact=email).exists()
    if password == password_conf:
        pass_safe = True
    else:
        pass_safe = False
        messages.add_message(
                request,
                messages.INFO,
                'Passwords do not match.',
                extra_tags='alert-danger registration_form'
            )
    if username_match:
        messages.add_message(
                request,
                messages.INFO,
                'An account with this username already exists,\
                        please choose a different one.',
                extra_tags='alert-danger registration_form'
            )
    if len(password) < 5:
        messages.add_message(
                request,
                messages.INFO,
                'Your password is too short, \
                        it should be at least 5 characters long.',
                extra_tags='alert-danger registration_form'
            )
    if email_match:
        messages.add_message(
                request,
                messages.INFO,
                'An account with this email already exists, \
                        please user a different one.',
                extra_tags='alert-danger registration_form'
            )
    utype_match = True
    if utype not in settings.VALID_GROUPS:
        utype_match = False
        messages.add_message(
                request,
                messages.INFO,
                'The given UserType is invalid, please choose from the menu.',
                extra_tags='alert-danger registration_form'
            )
    # return if signup is invalid
    # Check username, email,password, group
    if username_match == True or email_match == True or pass_safe == False\
            or utype_match == False:
        return redirect('user:register')

    # if all checks pass, proceed
    AssociatedGroup = Group.objects.get(name=utype)  # Get group
    user = User.objects.create_user(
            username=username,
            email=email,
            password=password
    )
    user.first_name = first
    user.last_name = last
    user.save()
    AssociatedGroup.user_set.add(user)
    #
    token = account_activation_token.make_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    #
    mail_subject = 'Account activation.'
    message = render_to_string('registration/email_account_activation.html', {
        'user': user,
        'domain': '127.0.0.1:8000',
        'uid': uid,
        'token': token,
    })
    to_email = user.email
    send_mail(
        mail_subject,
        message,
        'admin@practicepractice.net',
        [to_email],
        fail_silently=False,
    )
    messages.add_message(
            request,
            messages.INFO,
            'Your account has been created sucessfully, \
                    check your email for the confimration link.',
            extra_tags='alert-success login_form'
        )
    messages.add_message(
            request,
            messages.INFO,
            'You will not be able to login until \
                    confirmation is complete!',
            extra_tags='alert-warning login_form'
        )
    return redirect('user:login')


# activate user account action
def _activate(request, uidb64, token):
    _logoutUser(request)
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
        messages.add_message(
                request,
                messages.INFO,
                "The user to be confirmed does not exist for some reason, \
                        try creating another account!",
                extra_tags='alert-danger registration_form'
            )
    if user is not None and account_activation_token.check_token(user, token):
        try:
            u_profile = UserProfile.objects.get(user=user)
        except Exception:
            u_profile = UserProfile.objects.create(user_id=user.id)
        u_profile.registration = 1
        u_profile.save()
        messages.add_message(
                request,
                messages.INFO,
                "Confirmation is a sucess, you can now login!",
                extra_tags='alert-success login_form'
            )
        return redirect('user:login')
    else:
        messages.add_message(
                request,
                messages.INFO,
                "User Cannot be confirmed",
                extra_tags='alert-danger registration_form'
            )
        return redirect('user:register')


# Logout user view
def _logoutUser(request):
    logout(request)
    messages.add_message(
            request,
            messages.INFO,
            "Successfull logout!",
            extra_tags='alert-success top_homepage'
        )
    return redirect('main:index')
