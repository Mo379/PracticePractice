import re
from django.conf import settings
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.views import generic
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.core.mail import send_mail
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.utils.functional import cached_property
from view_breadcrumbs import BaseBreadcrumbMixin
from django.contrib.auth.models import Group
from datetime import datetime
from user.models import User
from user.util.GeneralUtil import account_activation_token, password_reset_token
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from user.forms import LoginForm, ForgotPasswordForm


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
        return 'user_profile'


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
        loginform = LoginForm()
        context = {}
        context['form_login'] = loginform
        return context


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
        forgotpasswordform = ForgotPasswordForm()
        context = {}
        context['form_password'] = forgotpasswordform
        return context


class DeleteAccountView(BaseBreadcrumbMixin, generic.ListView):
    template_name = "registration/delete_account.html"
    context_object_name = 'context'

    @cached_property
    def crumbs(self):
        return [
                ]

    def get_queryset(self):
        if self.request.user.is_authenticated:
            _logoutUser(self.request)
        context = {}
        context['uidb64'] = self.kwargs['uidb64']
        context['token'] = self.kwargs['token']
        return context


class PwdResetView(BaseBreadcrumbMixin, generic.ListView):
    template_name = "registration/password_reset_form.html"
    context_object_name = 'context'

    @cached_property
    def crumbs(self):
        return [
                ("forgot-password", reverse("user:forgot-password")),
                ("Password-Reset", '')
                ]

    def get_queryset(self):
        context = {}
        context['uidb64'] = self.kwargs['uidb64']
        context['token'] = self.kwargs['token']
        return context


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


#login 
def _loginUser(request):
    username = request.POST['username']
    password = request.POST['password']

    # chcking if user exits
    user = User.objects.filter(email__iexact=username).exists()
    # Email check
    if user:
        user = User.objects.get(email__iexact=username)
    else:
        # Username check
        user = User.objects.filter(username__iexact=username).exists()
        if user:
            user = User.objects.get(username__iexact=username)
        else:
            messages.add_message(
                    request,
                    messages.INFO,
                    'User does not exist.',
                    extra_tags='alert-danger login_form'
                )
            return redirect('user:login')
    # Authenticating the user
    auth = authenticate(request, username=user.username, password=password)
    # Chekcing if the user is registered
    try:
        registration = user.registration
    except Exception:
        registration = False
    if registration == False and user.is_superuser == False:
        messages.add_message(
                request,
                messages.INFO,
                'Registration is required before a login is allowed.',
                extra_tags='alert-danger login_form'
            )
    # checking if the user authentication is correct
    if auth is None:
        messages.add_message(
                request,
                messages.INFO,
                'Incorrect details, plese try again or create an account.',
                extra_tags='alert-danger login_form'
            )
    # checking if the user is in the password reset state
    try:
        pass_set = user.password_set
    except Exception:
        pass_set = False
    if pass_set == False and user.is_superuser == False:
        messages.add_message(
                request,
                messages.INFO,
                'You have to reset your password first!',
                extra_tags='alert-danger login_form'
            )
    # executing checks
    if auth is not None and (
            (pass_set == True and registration == True)
            or user.is_superuser == True):
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
    passlen_check = True
    if len(password) < 5:
        passlen_check = False
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
            or utype_match == False or passlen_check == False:
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


def _updatepassword(request):
    pass_current = request.POST['pass_current']
    pass_new = request.POST['pass_new']
    pass_conf = request.POST['pass_conf']
    #
    auth = authenticate(request, username=request.user.username, password=pass_current)
    auth_conf = True
    if auth is None:
        auth_conf = False
        messages.add_message(
                request,
                messages.INFO,
                'The current password cannot be confirmed.',
                extra_tags='alert-danger user_security'
            )
    pass_match = True
    if pass_new != pass_conf:
        pass_match = False
        messages.add_message(
                request,
                messages.INFO,
                'Passwords do not match.',
                extra_tags='alert-danger user_security'
            )
    pass_conf = True
    if len(pass_new) < 5:
        pass_conf = False
        messages.add_message(
                request,
                messages.INFO,
                'Your password is too short, \
                        it should be at least 5 characters long.',
                extra_tags='alert-danger user_security'
            )
    old_new_conf = True
    if pass_current == pass_new:
        old_new_conf = False
        messages.add_message(
                request,
                messages.INFO,
                'Old and new passwords cannot be the same.',
                extra_tags='alert-danger user_security'
            )

    if auth_conf == False or pass_match == False or \
            pass_conf == False or old_new_conf == False:
        return redirect('user:security')
    user = User.objects.get(username__iexact=request.user.username)
    user.set_password(pass_new)
    user.save()
    messages.add_message(
            request,
            messages.INFO,
            'Your Password was successfully updated!',
            extra_tags='alert-success user_security'
        )
    return redirect('user:security')


def _pwdreset_form(request):
    username = request.POST['username']
    # checking if user exists
    # check email
    user = User.objects.filter(email__iexact=username).exists()
    if user:
        user = User.objects.get(email__iexact=username)
    else:
        # check username
        user = User.objects.filter(username__iexact=username).exists()
        if user:
            user = User.objects.get(username__iexact=username)
        else:
            messages.add_message(
                    request,
                    messages.INFO,
                    'User does not exist.',
                    extra_tags='alert-danger pwdreset_form'
                )
            return redirect('user:forgot-password')
    # admins cannot do this
    if user.is_superuser:
            messages.add_message(
                    request,
                    messages.INFO,
                    'Admins cannot reset password, please contact main admin.',
                    extra_tags='alert-danger pwdreset_form'
                )
            return redirect('user:forgot-password')
    # Activating the password reset sequence
    user.password_set = False
    user.save()
    # send email
    token = password_reset_token.make_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    #
    mail_subject = 'Password Reset'
    message = render_to_string('registration/email_password_reset.html', {
        'user': user,
        'domain': '127.0.0.1:8000',
        'uid': uid,
        'token': token,
    })
    to_email = user.email
    try:
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
                'Please check your email for the password reset instructions.',
                extra_tags='alert-success pwdreset_form'
            )
        return redirect('user:forgot-password')
    except Exception:
        messages.add_message(
                request,
                messages.INFO,
                'Cannot send Email, please contact admin.',
                extra_tags='alert-danger pwdreset_form'
            )
        return redirect('user:forgot-password')


def _pwdreset(request):
    # post variables
    uidb64 = request.POST['uidb64']
    token = request.POST['token']
    new_pass = request.POST['password']
    new_pass_conf = request.POST['password_conf']
    # error cehcking
    pass_check = True
    if new_pass != new_pass_conf:
        pass_check = False
        messages.add_message(
                request,
                messages.INFO,
                'Passwords do not match.',
                extra_tags='alert-danger second_pwdreset_form'
            )
    passlen_check = True
    if len(new_pass) < 5:
        passlen_check = False
        messages.add_message(
                request,
                messages.INFO,
                'Your password is too short, \
                        it should be at least 5 characters long.',
                extra_tags='alert-danger second_pwdreset_form'
            )
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except Exception:
        user = None
        messages.add_message(
                request,
                messages.INFO,
                'User is invalid',
                extra_tags='alert-danger second_pwdreset_form'
            )
    super_check = True
    if user and user.is_superuser:
        super_check = False
        messages.add_message(
                request,
                messages.INFO,
                'User is invalid',
                extra_tags='alert-danger second_pwdreset_form'
            )
        return redirect('user:pwdreset', uidb64=uidb64, token=token)
    token_check = True
    if password_reset_token.check_token(user, token) == False:
        token_check = False
        messages.add_message(
                request,
                messages.INFO,
                'Password reset link is invalid, \
                        please request a new password reset.',
                extra_tags='alert-danger second_pwdreset_form'
            )
    #
    if user and token_check and pass_check and super_check and passlen_check:
        # reset password
        try:
            user.set_password(new_pass)
            user.password_set = True
            user.save()
            # update pass_set settings
            messages.add_message(
                    request,
                    messages.INFO,
                    'Your password has been reset, you can now login using the\
                            new password!',
                    extra_tags='alert-success login_form'
                )
            return redirect('user:login')
        except Exception:
            messages.add_message(
                    request,
                    messages.INFO,
                    'An unknonw error has occured please contact support \
                            (see contact page).',
                    extra_tags='alert-danger second_pwdreset_form'
                )
            return redirect('user:pwdreset', uidb64=uidb64, token=token)
    else:
        return redirect('user:pwdreset', uidb64=uidb64, token=token)


def _deleteaccount_1(request):
    user = request.user
    token = account_activation_token.make_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    #
    mail_subject = 'Account deletions.'
    message = render_to_string('registration/email_account_deletion.html', {
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
    _logoutUser(request)
    messages.add_message(
            request,
            messages.INFO,
            'A link containing instructions for account deletion has been \
                    sent to your registered Email.',
            extra_tags='alert-warning user_security'
        )
    return redirect('user:security')


def _deleteaccount_2(request):
    #
    uidb64 = request.POST['uidb64']
    token = request.POST['token']
    username = request.POST['username']
    password = request.POST['password']
    #
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
                extra_tags='alert-danger top_homepage'
            )
    if User.objects.filter(username__iexact=username).exists():
        auth = authenticate(
                request,
                username=user.username,
                password=password
            )
    else:
        auth = None
    if user is not None and account_activation_token.check_token(user, token) \
            and auth is not None:
        user.delete()
        messages.add_message(
                request,
                messages.INFO,
                'Your account has been deleted!',
                extra_tags='alert-danger top_homepage'
            )
        return redirect('main:index')
    else:
        messages.add_message(
                request,
                messages.INFO,
                "User Cannot be confirmed",
                extra_tags='alert-danger deleteaccount2'
            )
        return redirect('user:deleteaccount', uidb64=uidb64, token=token)


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
        user.registration = 1
        user.save()
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


def _accountdetails(request):
    username = request.POST['username']
    first_name = request.POST['first_name']
    last_name = request.POST['last_name']
    email = request.POST['email']
    date_of_birth = request.POST['date_of_birth']
    bio = request.POST['bio']
    # username check
    username_match = User.objects.filter(username__iexact=username).exists()
    username_check = True
    if (username_match and username.lower() != request.user.username.lower()) or \
            re.match(r'^[A-Za-z0-9_]+$', username) is None:
        username_check = False
        messages.add_message(
                request,
                messages.INFO,
                'The username entered already exists or is invalid!, \
                        please try again.',
                extra_tags='alert-danger user_profile'
            )
    # first name check
    name_check = True
    if re.match(r'^[A-Za-z]+$', first_name) is None and \
            re.match(r'^[A-Za-z]+$', last_name):
        name_check = False
        messages.add_message(
                request,
                messages.INFO,
                'The name entered is invalid, please try again.',
                extra_tags='alert-danger user_profile'
            )
    # email check
    email_match = User.objects.filter(email__iexact=email).exists()
    email_check = True
    if (email_match and request.user.email.lower() != email.lower()) \
            or re.match(r'^[A-Za-z0-9_@.]+$', email) is None:
        email_check = False
        messages.add_message(
                request,
                messages.INFO,
                'The email entered is invalid, please try again.',
                extra_tags='alert-danger user_profile'
            )
    # dob check
    dob_check = True
    try:
        datetime.strptime(date_of_birth, '%Y-%m-%d')
    except Exception:
        dob_check = False
        messages.add_message(
                request,
                messages.INFO,
                'The entered date of birth is invalid, please try again.'+str(date_of_birth),
                extra_tags='alert-danger user_profile'
            )
    # bio check
    bio_check = True
    if len(bio) > 500 or len(bio) < 25 or re.match(r'^[A-Za-z0-9_.,]+$', bio):
        bio_check = False
        messages.add_message(
                request,
                messages.INFO,
                'Your Bio is either invalid;\
                        25-500 characters and alphanumeric.',
                extra_tags='alert-danger user_profile'
            )
        
    #
    if username_check == False or name_check == False or email_check == False\
            or dob_check == False or bio_check == False:
        return redirect('user:index')
    #
    user = User.objects.get(pk=request.user.id)
    user.username = username
    user.first_name = first_name
    user.last_name = last_name
    user.email = email
    user.date_of_birth = date_of_birth
    user.bio = bio
    user.account_details_complete = True
    user.save()
    messages.add_message(
            request,
            messages.INFO,
            'Your account (Profile) details were sucessfully updated!',
            extra_tags='alert-success user_profile'
        )
    return redirect('user:index')


def _admindetails(request):
    messages.add_message(
            request,
            messages.INFO,
            'Your account (Admin) details were sucessfully updated!',
            extra_tags='alert-success user_profile'
        )
    return redirect('user:index')


def _studentdetails(request):
    messages.add_message(
            request,
            messages.INFO,
            'Your account (Student) details were sucessfully updated!',
            extra_tags='alert-success user_profile'
        )
    return redirect('user:index')


def _teacherdetails(request):
    messages.add_message(
            request,
            messages.INFO,
            'Your account (Teach) details were sucessfully updated!',
            extra_tags='alert-success user_profile'
        )
    return redirect('user:index')


def _organisationdetails(request):
    street_number = request.POST['org_street_number']
    street_name = request.POST['org_street_name']
    town = request.POST['org_town']
    post_code = request.POST['org_post_code']
    city = request.POST['org_city']
    country = request.POST['org_country']
    incorporation_date= request.POST['org_date']
    url = request.POST['org_url']
    # check street number
    streetnum_check = True
    # check street name
    streetname_check = True
    # check town
    town_check = True
    # check post_code
    postcode_check = True
    # check city
    city_check = True
    # check country
    country_check = True
    # check incorporation date
    incorp_check = True
    # check url
    url_check = True
    #
    if streetnum_check == False or streetname_check == False or \
            town_check == False or postcode_check == False or \
            city_check == False or country_check == False or \
            incorp_check == False or url_check == False:
                return redirect('user:index')
    messages.add_message(
            request,
            messages.INFO,
            'Your account (Organisation) details were sucessfully updated!'+str(request.POST),
            extra_tags='alert-success user_profile'
        )
    return redirect('user:index')


def _educatordetails(request):
    messages.add_message(
            request,
            messages.INFO,
            'Your account (Educator) details were sucessfully updated!',
            extra_tags='alert-success user_profile'
        )
    return redirect('user:index')


def _editordetails(request):
    messages.add_message(
            request,
            messages.INFO,
            'Your account (Editor) details were sucessfully updated!',
            extra_tags='alert-success user_profile'
        )
    return redirect('user:index')


def _affiliatedetails(request):
    messages.add_message(
            request,
            messages.INFO,
            'Your account (Affiliate) details were sucessfully updated!',
            extra_tags='alert-success user_profile'
        )
    return redirect('user:index')


def _themechange(request):
    new_theme = request.POST['theme']
    choices = [x[0] for x in request.user.CHOICES_THEME]
    if new_theme not in choices:
        messages.add_message(
                request,
                messages.INFO,
                'Theme cannot be found, nothing has changed.',
                extra_tags='alert-danger user_settings'
            )
        return redirect('user:settings')
    user = User.objects.get(pk=request.user.id)
    user.theme = new_theme
    user.save()
    messages.add_message(
            request,
            messages.INFO,
            'Your theme has been changed!',
            extra_tags='alert-success user_settings'
        )
    return redirect('user:settings')


def _languagechange(request):
    new_language = request.POST['language']
    choices = [x[0] for x in request.user.CHOICES_LANGUAGE]
    if new_language not in choices:
        messages.add_message(
                request,
                messages.INFO,
                'Language cannot be found, nothing has changed.',
                extra_tags='alert-danger user_settings'
            )
        return redirect('user:settings')
    user = User.objects.get(pk=request.user.id)
    user.language = new_language
    user.save()
    messages.add_message(
            request,
            messages.INFO,
            'Your theme has been changed!',
            extra_tags='alert-success user_settings'
        )
    return redirect('user:settings')


def _mailchoiceschange(request):
    choices = [i[0] for i in request.user.CHOICES_EMAIL]
    email_list = []
    for val in request.POST:
        if val in choices:
            if request.POST[val] == 'on':
                email_list.append(val)
    email_list.append('Core')
    user = User.objects.get(pk=request.user.id)
    user.mail_choices = email_list
    user.save()
    messages.add_message(
            request,
            messages.INFO,
            'Your mailing settings have been updated!',
            extra_tags='alert-success user_settings'
        )
    return redirect('user:settings')
