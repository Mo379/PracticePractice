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
from user.models import User, Organisation
from user.util.GeneralUtil import account_activation_token, password_reset_token
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from user.forms import (
        LoginForm,
        ForgotPasswordForm,
        RegistrationForm,
        ResetPasswordForm,
        ChangePasswordForm,
        EmailChoiceForm,
        AppearanceChoiceForm,
        LanguageChoiceForm,
        AccountDetailsForm,
        OrganisationDetailsForm,
    )


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
        user = User.objects.get(pk=self.request.user.id)
        organisation = Organisation.objects.get(user=user)
        #
        accountdetailsform = AccountDetailsForm(instance=user)
        organisationdetailsform = OrganisationDetailsForm(instance=organisation)
        loginform = LoginForm()
        #
        context = {}
        context['organisation'] = organisation
        context['form_login'] = loginform
        context['form_accountdetails'] = accountdetailsform
        context['form_admindetails'] = 's'
        context['form_studentdetails'] = 's'
        context['form_organisationdetails'] = organisationdetailsform
        context['form_educatordetails'] = 's'
        context['form_editordetails'] = 's'
        context['form_affiliatedetails'] = 's'
        return context


# Login view
class LoginView(BaseBreadcrumbMixin, generic.ListView):
    template_name = "user/registration/login.html"
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
    template_name = "user/registration/register.html"
    context_object_name = 'context'

    @cached_property
    def crumbs(self):
        return [
                ("register", reverse("user:register"))
                ]

    def get_queryset(self):
        registrationform = RegistrationForm()
        context = {}
        context['form_registration'] = registrationform
        return context
        return "user_settings"


# Forgot password view

class PwdResetView(BaseBreadcrumbMixin, generic.ListView):
    template_name = "user/registration/password_reset_form.html"
    context_object_name = 'context'

    @cached_property
    def crumbs(self):
        return [
                ("forgot-password", reverse("user:forgot-password")),
                ("Password-Reset", '')
                ]

    def get_queryset(self):
        resetpasswordform = ResetPasswordForm()
        context = {}
        context['uidb64'] = self.kwargs['uidb64']
        context['token'] = self.kwargs['token']
        context['form_resetpassword'] = resetpasswordform
        return context


class ForgotPasswordView(BaseBreadcrumbMixin, generic.ListView):
    template_name = "user/registration/forgot-password.html"
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
    template_name = "user/registration/delete_account.html"
    context_object_name = 'context'

    @cached_property
    def crumbs(self):
        return [
                ]

    def get_queryset(self):
        loginform = LoginForm()
        if self.request.user.is_authenticated:
            _logoutUser(self.request)
        context = {}
        context['uidb64'] = self.kwargs['uidb64']
        context['token'] = self.kwargs['token']
        context['form_deleteaccount'] = loginform
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
        changepasswordform = ChangePasswordForm()
        loginform = LoginForm()
        context = {}
        context['form_changepassword'] = changepasswordform
        context['form_login'] = loginform
        return context


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
        context = {}
        loginform = LoginForm()
        try:
            user = User.objects.get(pk=self.request.user.id)
            emailchoiceform = EmailChoiceForm(instance=user)
            appearancechoiceform = AppearanceChoiceForm(instance=user)
            languagechoiceform = LanguageChoiceForm(instance=user)
            context['form_emailchoice'] = emailchoiceform
            context['form_appearancechoice'] = appearancechoiceform
            context['form_languagechoice'] = languagechoiceform
        except Exception:
            context['form_login'] = loginform
        return context


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
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            # checking if the user authentication is correct
            # Log user in
            user = authenticate(request, username=username, password=password)
            if user:
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
                messages.add_message(
                        request,
                        messages.INFO,
                        'Incorrect details, please try again.',
                        extra_tags='alert-danger login_form'
                    )
        else:
            messages.add_message(
                    request,
                    messages.INFO,
                    'Something is wrong, please check that all' +
                    'inputs are valid.' + str(form.errors),
                    extra_tags='alert-danger login_form'
                )
    else:
        messages.add_message(
                request,
                messages.INFO,
                'Invalid Request Method',
                extra_tags='alert-danger login_form'
            )
    return redirect('user:login')


# Register user action
def _registerUser(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            utype = form.cleaned_data['usertype']
            password = form.cleaned_data['password']
            # Hash password
            user.set_password(password)
            user.save()
            # Give group
            AssociatedGroup = Group.objects.get(name=utype)  # Get group
            AssociatedGroup.user_set.add(user)
            # Email
            to_email = user.email
            mail_subject = 'Account activation.'
            mail_sender = 'admin@practicepractice.net'
            token = account_activation_token.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            message = render_to_string('user/emails/account_activation.html', {
                'user': user,
                'domain': '127.0.0.1:8000',
                'uid': uid,
                'token': token,
            })
            try:
                # send
                send_mail(
                    mail_subject,
                    message,
                    mail_sender,
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
            except Exception:
                messages.add_message(
                        request,
                        messages.INFO,
                        'An unexpected error has occurred, please try again.',
                        extra_tags='alert-warning login_form'
                    )
                return redirect('user:login')
        else:
            messages.add_message(
                    request,
                    messages.INFO,
                    'Something is wrong, please check that all inputs are valid.'+str(form.errors),
                    extra_tags='alert-danger registration_form'
                )
            return redirect('user:register')
    else:
        messages.add_message(
                request,
                messages.INFO,
                'Invalid Request Method',
                extra_tags='alert-danger registration_form'
            )
        return redirect('user:register')


# activate user account action


def _updatepassword(request):
    if request.method == 'POST':
        form = ChangePasswordForm(request.POST)
        if form.is_valid():
            pass_current = form.cleaned_data['password_current']
            pass_new = form.cleaned_data['password_new']
            user = authenticate(
                    request,
                    username=request.user.username,
                    password=pass_current
                )
            if user:
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
            else:
                messages.add_message(
                        request,
                        messages.INFO,
                        'The current password cannot be confirmed.',
                        extra_tags='alert-danger user_security'
                    )
        else:
            messages.add_message(
                    request,
                    messages.INFO,
                    'Something is wrong, please check that all inputs are valid.'+str(form.errors),
                    extra_tags='alert-danger user_security'
                )
    else:
        messages.add_message(
                request,
                messages.INFO,
                'Invalid Request Method',
                extra_tags='alert-danger user_security'
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
    message = render_to_string('user/emails/password_reset.html', {
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
    new_pass = request.POST['password_new']
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
    message = render_to_string('user/emails/account_deletion.html', {
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
    if request.method == "POST":
        organisation = Organisation.objects.get(user=request.user)
        form = OrganisationDetailsForm(
                request.POST or None,
                instance=organisation
            )
        if form.is_valid():
            form.save()
            messages.add_message(
                    request,
                    messages.INFO,
                    'Your account (Organisation) details were sucessfully updated!',
                    extra_tags='alert-success user_profile'
                )
        else:
            messages.add_message(
                    request,
                    messages.INFO,
                    'Something is wrong, please check that all inputs are valid.'+str(form.errors),
                    extra_tags='alert-danger user_profile'
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
    for val in request.POST.getlist('mail_choices'):
        if val in choices:
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
