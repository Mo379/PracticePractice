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
from user.models import (
        User,
        Admin,
        Student,
        Educator,
        Organisation,
        Editor,
        Affiliate
    )
from user.util.GeneralUtil import account_activation_token, password_reset_token
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.mixins import LoginRequiredMixin
from user.forms import (
        LoginForm,
        ForgotPasswordForm,
        RegistrationForm,
        ResetPasswordForm,
        ChangePasswordForm,
        DeleteAccountForm,
        EmailChoiceForm,
        AppearanceChoiceForm,
        LanguageChoiceForm,
        AccountDetailsForm,
        OrganisationDetailsForm,
        EducatorDetailsForm,
        AdminDetailsForm,
        StudentDetailsForm,
        EditorDetailsForm,
        AffiliateDetailsForm,
    )


# Create your views here.
class IndexView(LoginRequiredMixin, BaseBreadcrumbMixin, generic.ListView):
    login_url = 'user:login'
    redirect_field_name = None

    template_name = "user/index.html"
    context_object_name = 'context'

    @cached_property
    def crumbs(self):
        return [
                ("account", reverse("user:index")),
                ("profile", reverse("user:index"))
                ]

    def get_queryset(self):
        context = {}
        user = User.objects.get(pk=self.request.user.id)
        #
        admin = Admin.objects.get(user=user)
        student = Student.objects.get(user=user)
        organisation = Organisation.objects.get(user=user)
        educator = Educator.objects.get(user=user)
        editor = Editor.objects.get(user=user)
        affiliate = Affiliate.objects.get(user=user)
        #
        accountdetailsform = AccountDetailsForm(instance=user)
        admindetailsform = AdminDetailsForm(instance=admin)
        studentdetailsform = StudentDetailsForm(instance=student)
        organisationdetailsform = OrganisationDetailsForm(instance=organisation)
        educatordetailsform = EducatorDetailsForm(instance=educator)
        editordetailsform = EditorDetailsForm(instance=editor)
        affiliatedetailsform = AffiliateDetailsForm(instance=affiliate)
        #
        loginform = LoginForm()
        #
        context['organisation'] = organisation
        context['form_accountdetails'] = accountdetailsform
        context['form_admindetails'] = admindetailsform
        context['form_studentdetails'] = studentdetailsform
        context['form_organisationdetails'] = organisationdetailsform
        context['form_educatordetails'] = educatordetailsform
        context['form_editordetails'] = editordetailsform
        context['form_affiliatedetails'] = affiliatedetailsform
        #
        context['form_login'] = loginform
        return context


# Login view
class LoginView(BaseBreadcrumbMixin, generic.ListView):
    template_name = "user/registration/login.html"
    redirect_field_name = None
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
        resetpasswordform = ResetPasswordForm(
                    self.kwargs['uidb64'],
                    self.kwargs['token']
                )
        context = {}
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
        deleteaccountform = DeleteAccountForm(
                self.kwargs['uidb64'],
                self.kwargs['token']
                )
        if self.request.user.is_authenticated:
            logout(self.request)
        context = {}
        context['form_deleteaccount'] = deleteaccountform
        return context


# Billing view
class BillingView(LoginRequiredMixin, BaseBreadcrumbMixin, generic.ListView):
    login_url = 'user:login'
    redirect_field_name = None
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
class SecurityView(LoginRequiredMixin, BaseBreadcrumbMixin, generic.ListView):
    login_url = 'user:login'
    redirect_field_name = None

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
class SettingsView(LoginRequiredMixin, BaseBreadcrumbMixin, generic.ListView):
    login_url = 'user:login'
    redirect_field_name = None

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
                    'Something is wrong, please check that all ' +
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
    if request.method == 'POST':
        form = ForgotPasswordForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            user = User.objects.get(username=username)
            token = password_reset_token.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
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
            except Exception:
                messages.add_message(
                        request,
                        messages.INFO,
                        'Cannot send Email, please contact admin.',
                        extra_tags='alert-danger pwdreset_form'
                    )
        else:
            messages.add_message(
                    request,
                    messages.INFO,
                    'Something is wrong, please check that all inputs are valid.'+str(form.errors),
                    extra_tags='alert-danger pwdreset_form'
                )
    else:
        messages.add_message(
                request,
                messages.INFO,
                'Invalid Request Method',
                extra_tags='alert-danger pwdreset_form'
            )
    return redirect('user:forgot-password')


def _pwdreset(request):
    if request.method == 'POST':
        form = ResetPasswordForm(
                request.POST['uidb64'],
                request.POST['token'],
                request.POST,
            )
        if form.is_valid():
            uid = form.cleaned_data['uidb64']
            new_pass = form.cleaned_data['password_new']
            try:
                user = User.objects.get(pk=uid)
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
        else:
            messages.add_message(
                    request,
                    messages.INFO,
                    'Something is wrong, please check that ' +
                    'all inputs are valid.'+str(form.errors),
                    extra_tags='alert-danger second_pwdreset_form'
                )
    else:
        messages.add_message(
                request,
                messages.INFO,
                'Invalid Request Method',
                extra_tags='alert-danger second_pwdreset_form'
            )
    return redirect(
            'user:pwdreset',
            uidb64=request.POST['uidb64'],
            token=request.POST['token']
        )


def _deleteaccount_1(request):
    try:
        # does not use a form
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
                        sent to your registered Email, if this was an accident\
                        you can simply delete the email we sent and log back in.',
                extra_tags='alert-warning user_security'
            )
    except Exception:
        messages.add_message(
                request,
                messages.INFO,
                'An unknown error has occurred, please contact us.',
                extra_tags='alert-warning user_security'
            )
    return redirect('user:security')


def _deleteaccount_2(request):
    if request.method == 'POST':
        form = DeleteAccountForm(
                request.POST['uidb64'],
                request.POST['token'],
                request.POST
            )
        if form.is_valid():
            #
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            #
            try:
                user = authenticate(
                        request,
                        username=username,
                        password=password
                    )
                user.delete()
                messages.add_message(
                        request,
                        messages.INFO,
                        'Your account has been deleted, \
                                along with all of your data!',
                        extra_tags='alert-danger top_homepage'
                    )
                return redirect('main:index')
            except Exception:
                messages.add_message(
                        request,
                        messages.INFO,
                        'Incorrect information please try again.',
                        extra_tags='alert-danger deleteaccount2'
                    )
        else:
            messages.add_message(
                    request,
                    messages.INFO,
                    'Something is wrong, please check that ' +
                    'all inputs are valid.'+str(form.errors),
                    extra_tags='alert-danger deleteaccount2'
                )
    else:
        messages.add_message(
                request,
                messages.INFO,
                'Invalid Request Method',
                extra_tags='alert-danger deleteaccount2'
            )
    return redirect(
            'user:deleteaccount',
            uidb64=request.POST['uidb64'],
            token=request.POST['token']
        )


def _activate(request, uidb64, token):
    # Does not use a form
    logout(request)
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
    try:
        logout(request)
        messages.add_message(
                request,
                messages.INFO,
                "Successfull logout!",
                extra_tags='alert-success top_homepage'
            )
    except Exception:
        messages.add_message(
                request,
                messages.INFO,
                "Nothing to do!",
                extra_tags='alert-warning top_homepage'
            )
    return redirect('main:index')


def _accountdetails(request):
    if request.method == 'POST':
        # dont allow the email to change
        # the input email is overridden by the registered email
        request.POST = request.POST.copy()
        request.POST['email'] = request.user.email
        form = AccountDetailsForm(
                request.POST,
                request.FILES,
                instance=request.user
            )
        if form.is_valid():
            # make sure username is not the same
            # username check
            username = form.cleaned_data['username']
            # check user name is new and unique
            username_match = User.objects.filter(username__iexact=username).exists()
            if (
                username_match and
                username.lower() != request.user.username.lower()
            ):
                form.add_error(
                    'username',
                    ValidationError(
                        'An account with this username ' +
                        'already exits or is the same as your current username.'
                    )
                )
            else:
                form.save()
                request.user.account_details_complete = True
                request.user.save()
                messages.add_message(
                        request,
                        messages.INFO,
                        'Your account (Profile) details were sucessfully updated!',
                        extra_tags='alert-success user_profile'
                    )
        else:
            messages.add_message(
                    request,
                    messages.INFO,
                    'Something is wrong, please check that all inputs are valid.'+str(form.errors),
                    extra_tags='alert-danger user_profile'
                )
    else:
        messages.add_message(
                request,
                messages.INFO,
                'Invalid Request Method',
                extra_tags='alert-danger user_profile'
            )
    return redirect('user:index')


def _admindetails(request):
    if request.method == 'POST':
        admin, was_created = Admin.objects.get_or_create(user=request.user)
        form = AdminDetailsForm(request.POST, instance=admin)
        if form.is_valid():
            form.save()
            request.user.group_details_complete = True
            request.user.save()
            messages.add_message(
                    request,
                    messages.INFO,
                    'Your account (Admin) details were sucessfully updated!',
                    extra_tags='alert-success user_profile'
                )
        else:
            messages.add_message(
                    request,
                    messages.INFO,
                    'Something is wrong, please check that all inputs are valid.'+str(form.errors),
                    extra_tags='alert-danger user_profile'
                )
    else:
        messages.add_message(
                request,
                messages.INFO,
                'Invalid Request Method',
                extra_tags='alert-danger user_profile'
            )
    return redirect('user:index')


def _studentdetails(request):
    if request.method == 'POST':
        student, was_created = Student.objects.get_or_create(user=request.user)
        form = StudentDetailsForm(request.POST, instance=student)
        if form.is_valid():
            form.save()
            request.user.group_details_complete = True
            request.user.save()
            messages.add_message(
                    request,
                    messages.INFO,
                    'Your account (Student) details were sucessfully updated!',
                    extra_tags='alert-success user_profile'
                )
        else:
            messages.add_message(
                    request,
                    messages.INFO,
                    'Something is wrong, please check that all inputs are valid.'+str(form.errors),
                    extra_tags='alert-danger user_profile'
                )
    else:
        messages.add_message(
                request,
                messages.INFO,
                'Invalid Request Method',
                extra_tags='alert-danger user_profile'
            )
    return redirect('user:index')


def _educatordetails(request):
    if request.method == 'POST':
        educator, was_created = Educator.objects.get_or_create(user=request.user)
        form = EducatorDetailsForm(request.POST, instance=educator)
        if form.is_valid():
            form.save()
            request.user.group_details_complete = True
            request.user.save()
            messages.add_message(
                    request,
                    messages.INFO,
                    'Your account (Educator) details were sucessfully updated!',
                    extra_tags='alert-success user_profile'
                )
        else:
            messages.add_message(
                    request,
                    messages.INFO,
                    'Something is wrong, please check that all inputs are valid.'+str(form.errors),
                    extra_tags='alert-danger user_profile'
                )
    else:
        messages.add_message(
                request,
                messages.INFO,
                'Invalid Request Method',
                extra_tags='alert-danger user_profile'
            )
    return redirect('user:index')


def _organisationdetails(request):
    if request.method == "POST":
        organisation = Organisation.objects.get(user=request.user)
        form = OrganisationDetailsForm(
                request.POST or None,
                request.FILES,
                instance=organisation
            )
        if form.is_valid():
            form.save()
            request.user.group_details_complete = True
            request.user.save()
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


def _editordetails(request):
    if request.method == 'POST':
        editor, was_created = Editor.objects.get_or_create(user=request.user)
        form = EditorDetailsForm(request.POST, request.FILES, instance=editor)
        if form.is_valid():
            form.save()
            request.user.group_details_complete = True
            request.user.save()
            messages.add_message(
                    request,
                    messages.INFO,
                    'Your account (Editor) details were sucessfully updated!',
                    extra_tags='alert-success user_profile'
                )
        else:
            messages.add_message(
                    request,
                    messages.INFO,
                    'Something is wrong, please check that all ' +
                    'inputs are valid.'+str(form.errors),
                    extra_tags='alert-danger user_profile'
                )
    else:
        messages.add_message(
                request,
                messages.INFO,
                'Invalid Request Method',
                extra_tags='alert-danger user_profile'
            )
    return redirect('user:index')


def _affiliatedetails(request):
    if request.method == 'POST':
        affiliate, was_created = Affiliate.objects.get_or_create(user=request.user)
        form = AffiliateDetailsForm(request.POST, request.FILES, instance=affiliate)
        if form.is_valid():
            form.save()
            request.user.group_details_complete = True
            request.user.save()
            messages.add_message(
                    request,
                    messages.INFO,
                    'Your account (Affiliate) details were sucessfully updated!',
                    extra_tags='alert-success user_profile'
                )
        else:
            messages.add_message(
                    request,
                    messages.INFO,
                    'Something is wrong, please check that all ' +
                    'inputs are valid.'+str(form.errors),
                    extra_tags='alert-danger user_profile'
                )
    else:
        messages.add_message(
                request,
                messages.INFO,
                'Invalid Request Method',
                extra_tags='alert-danger user_profile'
            )
    return redirect('user:index')


def _themechange(request):
    if request.method == 'POST':
        form = AppearanceChoiceForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.add_message(
                    request,
                    messages.INFO,
                    'Your preffered theme was successfully updated ' +
                    '(Try to refresh your browser if no changes show).',
                    extra_tags='alert-success user_settings'
                )
        else:
            messages.add_message(
                    request,
                    messages.INFO,
                    'Something is wrong, please check that all inputs are valid.'+str(form.errors),
                    extra_tags='alert-danger user_settings'
                )
    else:
        messages.add_message(
                request,
                messages.INFO,
                'Invalid Request Method',
                extra_tags='alert-danger user_settings'
            )
    return redirect('user:settings')


def _languagechange(request):
    if request.method == 'POST':
        form = LanguageChoiceForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.add_message(
                    request,
                    messages.INFO,
                    'Your preffered language was successfully updated.',
                    extra_tags='alert-success user_settings'
                )
        else:
            messages.add_message(
                    request,
                    messages.INFO,
                    'Something is wrong, please check that all inputs are valid.'+str(form.errors),
                    extra_tags='alert-danger user_settings'
                )
    else:
        messages.add_message(
                request,
                messages.INFO,
                'Invalid Request Method',
                extra_tags='alert-danger user_settings'
            )
    return redirect('user:settings')


def _mailchoiceschange(request):
    if request.method == 'POST':
        request.POST = request.POST.copy()
        form = EmailChoiceForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.add_message(
                    request,
                    messages.INFO,
                    'Your preffered Email types were successfully updated.',
                    extra_tags='alert-success user_settings'
                )
        else:
            messages.add_message(
                    request,
                    messages.INFO,
                    'Something is wrong, please check that all inputs are valid.'+str(form.errors),
                    extra_tags='alert-danger user_settings'
                )
    else:
        messages.add_message(
                request,
                messages.INFO,
                'Invalid Request Method',
                extra_tags='alert-danger user_settings'
            )
    return redirect('user:settings')
