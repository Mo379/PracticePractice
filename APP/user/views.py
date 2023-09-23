import os
import re
import json
from django.conf import settings
from django.apps import apps, AppConfig
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.views import generic
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.utils.functional import cached_property
from view_breadcrumbs import BaseBreadcrumbMixin
from django.contrib.auth.models import Group
from datetime import datetime
from user.models import (
        User
    )
from user.util.GeneralUtil import account_activation_token, password_reset_token
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from PP2.mixin import LoginRequiredMixin
from user.forms import (
        LoginForm,
        ForgotPasswordForm,
        RegistrationForm,
        ResetPasswordForm,
        ChangePasswordForm,
        TriggerDeleteAccountForm,
        DeleteAccountForm,
        EmailChoiceForm,
        AppearanceChoiceForm,
        LanguageChoiceForm,
        AccountDetailsForm,
    )


# Create your views here.
import stripe
from django.db import transaction
from djstripe import webhooks
from djstripe.models import (
        Customer,
        PaymentMethod,
        Price,
        Subscription,
        Charge,
        Session
    )
import markdown
from django.db.models import Q
from io import BytesIO




@webhooks.handler("payment_intent.succeeded")
def my_handler(event, **kwargs):
    def do_something():
        print("We should probably notify the user at this pointsss")
    transaction.on_commit(do_something)


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
        accountdetailsform = AccountDetailsForm(instance=user)
        context['AccountDetailsForm'] = accountdetailsform
        # checking if billing information exists
        context['user_member_bool'] = Subscription.objects.filter(customer=user.id, status__in=['trialing', 'active'], livemode=settings.STRIPE_LIVE_MODE).exists()
        context['user_billing_bool'] = PaymentMethod.objects.filter(customer=user.id, livemode=settings.STRIPE_LIVE_MODE).exists()
        context['profile_picture_url'] = os.path.join(
                settings.CDN_URL,
                'users',
                str(user.id),
                'profile',
                'profile_picture'
            ) + f'_{str(user.profile_pic_ext)}'
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
        context = {}
        user = self.request.user
        # think about adding checks for robustness.
        context['publishable_key'] = settings.STRIPE_PUBLISHABLE_KEY
        #
        customer_object = Customer.objects.get(id=user.id, livemode=settings.STRIPE_LIVE_MODE)
        context['customer'] = customer_object
        #
        context['billing_history'] = Charge.objects.filter(customer=user.id, livemode=settings.STRIPE_LIVE_MODE)
        #
        payment_methods = list(PaymentMethod.objects.filter(customer=user.id, livemode=settings.STRIPE_LIVE_MODE))
        context['paymentmethods'] = payment_methods
        if Subscription.objects.filter(customer=user.id, status__in=['trialing', 'active'], livemode=settings.STRIPE_LIVE_MODE).exists():
            subscription = Subscription.objects.get(customer=user.id, status__in=['trialing', 'active'], livemode=settings.STRIPE_LIVE_MODE)
            context['subscription_status'] = subscription.status
            context['billing_interval'] = subscription.plan.interval
            if subscription.discount is not None:
                if 'coupon' in subscription.discount.keys():
                    discount_amount = float(subscription.plan.amount) * float(subscription.discount['coupon']['percent_off']/100)
                else:
                    discount_amount = 0
            else:
                discount_amount = 0
            context['billing_amount'] = round(float(subscription.plan.amount) - discount_amount, 2)
            context['billing_next'] = subscription.current_period_end
            context['plan_name'] = str(subscription.plan)
            context['cancel_later'] = subscription.cancel_at_period_end
        #
        return context


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
        triggeraccountdeleteform = TriggerDeleteAccountForm()
        loginform = LoginForm()
        context = {}
        context['form_changepassword'] = changepasswordform
        context['form_tad'] = triggeraccountdeleteform
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
class JoinView(LoginRequiredMixin, BaseBreadcrumbMixin, generic.ListView):
    login_url = 'user:login'
    redirect_field_name = None

    template_name = "user/join.html"
    context_object_name = 'context'

    @cached_property
    def crumbs(self):
        return [
                ("account", reverse("user:index")),
                ("join", reverse("user:join")),
                ]

    def get_queryset(self):
        context = {}
        context['publishable_key'] = settings.STRIPE_PUBLISHABLE_KEY
        return context


class JoinSuccess(LoginRequiredMixin, BaseBreadcrumbMixin, generic.ListView):
    login_url = 'user:login'
    redirect_field_name = None
    template_name = "user/joinsuccess.html"
    context_object_name = 'context'

    @cached_property
    def crumbs(self):
        return [
                ("account", reverse("user:index")),
                ("join", reverse("user:join")),
                ]

    def get_queryset(self):
        context = {}
        payment_session_id = self.kwargs['sessid']
        if Session.objects.filter(id=payment_session_id):
            session = Session.objects.get(id=payment_session_id)
            context['payment_session'] = session
        return context


class CancelSubscription(LoginRequiredMixin, BaseBreadcrumbMixin, generic.ListView):
    login_url = 'user:login'
    redirect_field_name = None
    template_name = "user/CancelSubscription.html"
    context_object_name = 'context'

    @cached_property
    def crumbs(self):
        return [
                ]

    def get_queryset(self):
        loginform = LoginForm()
        context = {}
        context['form_login'] = loginform
        return context


class AddPaymentMethodView(
            LoginRequiredMixin, BaseBreadcrumbMixin, generic.ListView
        ):
    login_url = 'user:login'
    redirect_field_name = None
    template_name = "user/payments/add_payment_method.html"
    context_object_name = 'context'

    @cached_property
    def crumbs(self):
        return [
                ("account", reverse("user:index")),
                ("billing", reverse("user:billing")),
            ]

    def get_queryset(self):
        context = {}
        # think about adding checks for robustness.
        stripe.api_key = settings.STRIPE_SECRET_KEY
        intent = stripe.SetupIntent.create(
                customer=str(self.request.user.id),
                payment_method_types=["card"],
          )
        context['client_secret'] = intent.client_secret
        context['publishable_key'] = settings.STRIPE_PUBLISHABLE_KEY
        return context


# Appearance View
# login
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
                        extra_tags='alert-success dashboard_index'
                    )
                # Redirect to a success page.
                return redirect('main:index')
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
def _contact_us(request):
    if request.method == "POST":
        full_name = request.user.first_name + ' ' + request.user.last_name
        message_subject = request.POST['message_subject']
        message = request.POST['message']
        captcha_response = request.POST['g-recaptcha-response']
        to_email = 'admin@practicepractice.net'
        data = {
            'secret': '6LezHSIoAAAAAMqd1S5XrTR5CoZ5C4ep6D7vY2Hl',
            'response': captcha_response,
        }
        import requests
        response = requests.post('https://www.google.com/recaptcha/api/siteverify', data=data)
        result = response.json()
        if result['success'] and request.user.is_authenticated:
            send_mail(
                message_subject,
                message + f'\n\n {request.user.email}',
                to_email,
                [to_email],
                fail_silently=False,
            )
            messages.add_message(
                    request,
                    messages.INFO,
                    'Your message has been recieved, \
                            check your email for the confimration.',
                    extra_tags='alert-success contact_form'
                )
        else:
            messages.add_message(
                    request,
                    messages.INFO,
                    'Sorry canot verify your identity.',
                    extra_tags='alert-warning contact_form'
                )
    return redirect('main:contact')


# Register user action
def _registerUser(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            password = form.cleaned_data['password']
            # Hash password
            user.set_password(password)
            user.save()
            AssociatedGroup = Group.objects.get(name='Student')  # Get group
            AssociatedGroup.user_set.add(user)
            # Email
            to_email = user.email
            mail_subject = 'Account activation.'
            mail_sender = 'admin@practicepractice.net'
            token = account_activation_token.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            message = render_to_string('user/emails/account_activation.html', {
                'user': user,
                'domain': settings.SITE_URL,
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


@login_required(login_url='/user/login', redirect_field_name=None)
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
                'domain': settings.SITE_URL,
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


@login_required(login_url='/user/login', redirect_field_name=None)
def _deleteaccount_1(request):
    if request.method == 'POST':
        form = TriggerDeleteAccountForm(request.POST)
        if form.is_valid():
            password = form.cleaned_data['password']
            user = authenticate(
                    request,
                    username=request.user.username,
                    password=password
                )
            if user:
                try:
                    #
                    token = account_activation_token.make_token(user)
                    uid = urlsafe_base64_encode(force_bytes(user.pk))
                    mail_subject = 'Account deletions.'
                    message = render_to_string('user/emails/account_deletion.html', {
                        'user': user,
                        'domain': settings.SITE_URL,
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
                                    sent to your registered Email, if this was an accident, \
                                    you can simply delete the email we sent and log back in.',
                            extra_tags='alert-warning login_form'
                        )
                    return redirect('user:login')
                except Exception:
                    messages.add_message(
                            request,
                            messages.INFO,
                            'An unknown error has occurred, please contact us.',
                            extra_tags='alert-warning user_security'
                        )
            else:
                messages.add_message(
                        request,
                        messages.INFO,
                        'Invalid details',
                        extra_tags='alert-warning user_security'
                    )
        else:
            messages.add_message(
                    request,
                    messages.INFO,
                    'Something is wrong, please check that ' +
                    'all inputs are valid.'+str(form.errors),
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
    if user is not None \
            and account_activation_token.check_token(user, token)\
            and user.registration==0:
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
                "User Cannot be confirmed, or is already registered.",
                extra_tags='alert-danger registration_form'
            )
        return redirect('user:register')


# Logout user view
@login_required(login_url='/user/login', redirect_field_name=None)
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


@login_required(login_url='/user/login', redirect_field_name=None)
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
            upload_image = form.cleaned_data['profile_upload']
            # Upload image
            if upload_image:
                file_name_list = upload_image.name.split('.')
                file_extension = file_name_list.pop(-1)
                full_name = '.'.join(file_name_list) + '.' + file_extension
                request.user.profile_pic_ext = full_name
                request.user.profile_pic_status = True
                request.user.save()
                if file_extension not in MDEDITOR_CONFIGS['upload_image_formats']:
                    messages.add_message(
                            request,
                            messages.INFO,
                            'Filetype is not allowed, please user: ' + str(','.join(MDEDITOR_CONFIGS['upload_image_formats'])),
                            extra_tags='alert-warning user_profile'
                        )
                else:
                    # save image
                    try:
                        f = BytesIO()
                        for chunk in upload_image.chunks():
                            f.write(chunk)
                        f.seek(0)
                        # get object location
                        file_key = f'users/{request.user.id}/profile/profile_picture_{full_name}'
                        settings.AWS_S3_C.upload_fileobj(
                                f,
                                settings.AWS_BUCKET_NAME,
                                file_key,
                                ExtraArgs={'ACL': 'public-read'}
                            )
                        request.user.profile_upload.delete()
                    except Exception as e:
                        messages.add_message(
                                request,
                                messages.INFO,
                                'Could not store your profile image.',
                                extra_tags='alert-warning user_profile'
                            )
            # check user name is new and unique
            taken_username_check = User.objects.filter(
                    ~Q(pk=request.user.id),
                    username__iexact=username
                ).exists()
            if (
                taken_username_check
            ):
                messages.add_message(
                        request,
                        messages.INFO,
                        'Username already exists, please chose a different one.',
                        extra_tags='alert-warning user_profile'
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


@login_required(login_url='/user/login', redirect_field_name=None)
def _themechange(request):
    if request.method == 'POST':
        form = AppearanceChoiceForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.add_message(
                    request,
                    messages.INFO,
                    'Your preferred theme was successfully updated ' +
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


@login_required(login_url='/user/login', redirect_field_name=None)
def _languagechange(request):
    if request.method == 'POST':
        form = LanguageChoiceForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.add_message(
                    request,
                    messages.INFO,
                    'Your preferred language was successfully updated.',
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


@login_required(login_url='/user/login', redirect_field_name=None)
def _mailchoiceschange(request):
    if request.method == 'POST':
        request.POST = request.POST.copy()
        form = EmailChoiceForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.add_message(
                    request,
                    messages.INFO,
                    'Your preferred Email types were successfully updated.',
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


@login_required(login_url='/user/login', redirect_field_name=None)
def _makedefaultpaymentmethod(request):
    if request.method == 'POST':
        request.POST = request.POST.copy()
        payment_methods = PaymentMethod.objects.filter(customer=str(request.user.id), livemode=settings.STRIPE_LIVE_MODE)
        payment_methods_ids = {method.id: method for method in payment_methods}
        new_default_method_id = request.POST['method_id']
        if new_default_method_id in payment_methods_ids:
            # do stripe defaulting
            stripe.api_key = settings.STRIPE_SECRET_KEY
            stripe.Customer.modify(
                    sid=str(request.user.id),
                    invoice_settings={'default_payment_method': str(new_default_method_id)}
              )
            # do local defaulting
            customer = Customer.objects.get(id=request.user.id, livemode=settings.STRIPE_LIVE_MODE)
            customer.default_payment_method=payment_methods_ids[str(new_default_method_id)]
            customer.save()
            messages.add_message(
                    request,
                    messages.INFO,
                    'Your default payment method has been updated.',
                    extra_tags='alert-success user_billing'
                )
        else:
            messages.add_message(
                    request,
                    messages.INFO,
                    'Invalid payment method.',
                    extra_tags='alert-danger user_billing'
                )
    else:
        messages.add_message(
                request,
                messages.INFO,
                'Invalid Request Method',
                extra_tags='alert-danger user_billing'
            )
    return redirect('user:billing')


@login_required(login_url='/user/login', redirect_field_name=None)
def _deletepaymentmethod(request):
    if request.method == 'POST':
        request.POST = request.POST.copy()
        payment_methods = PaymentMethod.objects.filter(customer=str(request.user.id), livemode=settings.STRIPE_LIVE_MODE)
        payment_methods_ids = {method.id: method for method in payment_methods}
        deleted_payment_method_id= request.POST['method_id']
        if deleted_payment_method_id in payment_methods_ids:
            method_object = payment_methods_ids[deleted_payment_method_id]
            customer = Customer.objects.get(id=request.user.id, livemode=settings.STRIPE_LIVE_MODE)
            if customer.default_payment_method != method_object or len(payment_methods_ids)==1:
                # do stripe deleting
                stripe.api_key = settings.STRIPE_SECRET_KEY
                stripe.PaymentMethod.detach(
                    deleted_payment_method_id,
                )
                PaymentMethod.objects.get(id=deleted_payment_method_id, livemode=settings.STRIPE_LIVE_MODE).delete()
                # do local deleting
                messages.add_message(
                        request,
                        messages.INFO,
                        'Your payment method has been deleted from all of our records.',
                        extra_tags='alert-success user_billing'
                    )
            else:
                messages.add_message(
                        request,
                        messages.INFO,
                        'You cannot remove your default payment method, unless it is the last one left.',
                        extra_tags='alert-danger user_billing'
                    )
        else:
            messages.add_message(
                    request,
                    messages.INFO,
                    'Invalid payment method.',
                    extra_tags='alert-danger user_billing'
                )
    else:
        messages.add_message(
                request,
                messages.INFO,
                'Invalid Request Method',
                extra_tags='alert-danger user_billing'
            )
    return redirect('user:billing')


@login_required(login_url='/user/login', redirect_field_name=None)
def _create_checkout_session(request):
    if request.method == 'POST':
        customer = Customer.objects.get(id=request.user.id, livemode=settings.STRIPE_LIVE_MODE)
        price_id = json.loads(request.body)['price_id']
        if Price.objects.filter(id=price_id, livemode=settings.STRIPE_LIVE_MODE).exists():
            # See if subscription exists or not
            if Subscription.objects.filter(
                        customer=request.user.id, status__in=['trialing', 'active'], livemode=settings.STRIPE_LIVE_MODE
                    ).exists() == False:
                # Set Stripe API key
                stripe.api_key = settings.STRIPE_SECRET_KEY
                # Create Stripe Checkout session
                checkout_session = stripe.checkout.Session.create(
                        payment_method_types=["card"],
                        mode="subscription",
                        line_items=[
                            {
                                "price": price_id,
                                "quantity": 1
                            }
                        ],
                        customer=customer.id,
                        success_url=settings.SITE_URL + f"/user/joinsuccess/{{CHECKOUT_SESSION_ID}}",
                        # The cancel_url is typically set to the original product page
                        cancel_url=settings.SITE_URL + f"/user/join",
                    )
                return JsonResponse({'sessionId': checkout_session['id'] if checkout_session else None})
            else:
                return JsonResponse({'error': "Subscription not allowed, you " +
                            "either already have a subscription or this subscription " +
                            "is't available for your account type."}
                        )
        else:
            return JsonResponse({'error': 'product does not exist.'})
    else:
        return JsonResponse({'error': 'Invalid Request Method.'})


@login_required(login_url='/user/login', redirect_field_name=None)
def _create_customer_portal_session(request):
    if request.method == 'POST':
        user = request.user
        stripe.api_key = settings.STRIPE_SECRET_KEY
        customer = Customer.objects.get(id=user.id, livemode=settings.STRIPE_LIVE_MODE)
        # Authenticate your user.
        session = stripe.billing_portal.Session.create(
            customer=f'{customer.id}',
            return_url='https://practicepractice.net',
        )
        return redirect(session.url)
    return render(request, 'main/index.html')
