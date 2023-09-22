import stripe
from PP2.utils import h_encode, h_decode
from functools import wraps
from django.conf import settings
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib import messages
from djstripe.models import (
        Customer,
        Subscription,
    )
from content.models import Course, CourseSubscription, CourseVersion


def stripe_customer_checks(user):
    if Customer.objects.filter(id=user.id, livemode=settings.STRIPE_LIVE_MODE).exists() is not True:
        stripe.api_key = settings.STRIPE_SECRET_KEY
        stripe.Customer.create(
                email=user.email,
                name=user.first_name+' '+user.last_name,
                id=user.id,
                metadata={'username': user.username}
            )


class LoginRequiredMixin:
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            stripe_customer_checks(request.user)
            return super().dispatch(request, *args, **kwargs)
        else:
            # Redirect to login page if user is not authenticated
            return HttpResponseRedirect(reverse('user:login'))


def AnySubscriptionRequiredDec(f):
    @wraps(f)
    def dispatch(request, *args, **kwargs):
        if request.user.is_authenticated:
            stripe_customer_checks(request.user)
            # Assuming you have a subscription model named Subscription
            admin_customer = Customer.objects.get(id=request.user.id, livemode=settings.STRIPE_LIVE_MODE)
            if Subscription.objects.filter(customer=admin_customer, status__in=['trialing', 'active'], livemode=settings.STRIPE_LIVE_MODE).exists():
                return f(request, *args, **kwargs)
            else:
                # Redirect to a page indicating subscription is required
                messages.add_message(
                        request,
                        messages.INFO,
                        'You need a subscription to be able to access this content, see the bottom of this page for the subscription packages.',
                        extra_tags='alert-warning top_homepage'
                    )
                return HttpResponseRedirect(reverse('main:index'))
        else:
            # Redirect to login page if user is not authenticated
            return HttpResponseRedirect(reverse('user:login'))
    return dispatch


class AnySubscriptionRequiredMixin:
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            stripe_customer_checks(request.user)
            # Assuming you have a subscription model named Subscription
            admin_customer = Customer.objects.get(id=request.user.id, livemode=settings.STRIPE_LIVE_MODE)
            if Subscription.objects.filter(customer=admin_customer, status__in=['trialing', 'active'], livemode=settings.STRIPE_LIVE_MODE).exists():
                return super().dispatch(request, *args, **kwargs)
            else:
                # Redirect to a page indicating subscription is required
                messages.add_message(
                        request,
                        messages.INFO,
                        'You need a subscription to be able to access this content, see the bottom of this page for the subscription packages.',
                        extra_tags='alert-warning top_homepage'
                    )
                return HttpResponseRedirect(reverse('main:index'))
        else:
            # Redirect to login page if user is not authenticated
            return HttpResponseRedirect(reverse('user:login'))


def AnySubscriptionRequiredDec(f):
    @wraps(f)
    def dispatch(request, *args, **kwargs):
        if request.user.is_authenticated:
            stripe_customer_checks(request.user)
            # Assuming you have a subscription model named Subscription
            admin_customer = Customer.objects.get(id=request.user.id, livemode=settings.STRIPE_LIVE_MODE)
            if Subscription.objects.filter(customer=admin_customer, status__in=['trialing', 'active'], livemode=settings.STRIPE_LIVE_MODE).exists():
                return f(request, *args, **kwargs)
            else:
                # Redirect to a page indicating subscription is required
                messages.add_message(
                        request,
                        messages.INFO,
                        'You need a subscription to be able to access this content, see the bottom of this page for the subscription packages.',
                        extra_tags='alert-warning top_homepage'
                    )
                return HttpResponseRedirect(reverse('main:index'))
        else:
            # Redirect to login page if user is not authenticated
            return HttpResponseRedirect(reverse('user:login'))
    return dispatch


class AISubscriptionRequiredMixin:
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            stripe_customer_checks(request.user)
            # Assuming you have a subscription model named Subscription
            admin_customer = Customer.objects.get(id=request.user.id, livemode=settings.STRIPE_LIVE_MODE)
            active_subscriptions = Subscription.objects.filter(customer=admin_customer, status__in=['trialing', 'active'], livemode=settings.STRIPE_LIVE_MODE)
            plan_description = str(active_subscriptions[0].plan) if len(active_subscriptions) > 0 else ''
            if 'with ai' in plan_description.lower():
                return super().dispatch(request, *args, **kwargs)
            else:
                # Redirect to a page indicating subscription is required
                messages.add_message(
                        request,
                        messages.INFO,
                        'You need a **with AI** subscription to be able to access this content, see the bottom of this page for the subscription packages.',
                        extra_tags='alert-warning top_homepage'
                    )
                return HttpResponseRedirect(reverse('main:index'))
        else:
            # Redirect to login page if user is not authenticated
            return HttpResponseRedirect(reverse('user:login'))


def AISubscriptionRequiredDec(f):
    @wraps(f)
    def dispatch(request, *args, **kwargs):
        if request.user.is_authenticated:
            stripe_customer_checks(request.user)
            admin_customer = Customer.objects.get(id=request.user.id, livemode=settings.STRIPE_LIVE_MODE)
            active_subscriptions = Subscription.objects.filter(customer=admin_customer, status__in=['trialing', 'active'], livemode=settings.STRIPE_LIVE_MODE)
            plan_description = str(active_subscriptions[0].plan) if len(active_subscriptions) > 0 else ''
            if 'with ai' in plan_description.lower():
                return f(request, *args, **kwargs)
            else:
                messages.add_message(
                    request,
                    messages.INFO,
                    'You need a **with AI** subscription to be able to access this content, see the bottom of this page for the subscription packages.',
                    extra_tags='alert-warning top_homepage'
                )
                return HttpResponseRedirect(reverse('main:index'))
        else:
            return HttpResponseRedirect(reverse('user:login'))
    return dispatch


class CourseSubscriptionRequiredMixin:
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            stripe_customer_checks(request.user)
            # Assuming you have a subscription model named Subscription
            course = Course.objects.get(pk=kwargs['course_id'])
            if CourseSubscription.objects.filter(user=request.user, course=course).exists():
                return super().dispatch(request, *args, **kwargs)
            else:
                # Redirect to a page indicating subscription is required
                messages.add_message(
                        request,
                        messages.INFO,
                        'You need to enroll for this course first!, you can do this for *free* by clicking the enroll button.',
                        extra_tags='alert-warning top_homepage'
                    )
                return HttpResponseRedirect(reverse('content:marketcourse', args=[course.id]))
        else:
            # Redirect to login page if user is not authenticated
            return HttpResponseRedirect(reverse('user:login'))


def CourseSubscriptionRequiredDec(f):
    @wraps(f)
    def dispatch(request, *args, **kwargs):
        if request.user.is_authenticated:
            stripe_customer_checks(request.user)
            # Assuming you have a subscription model named Subscription
            if 'course_id' in request.POST:
                course_id = request.POST['course_id']
                try:
                    course_id = int(course_id)
                except Exception:
                    course_id = h_decode(course_id)
                course = Course.objects.get(pk=course_id)
            elif 'course_version_id' in request.POST:
                version = CourseVersion.objects.get(pk=request.POST['course_version_id'])
                course = version.course
            #
            if CourseSubscription.objects.filter(user=request.user, course=course).exists():
                return f(request, *args, **kwargs)
            else:
                # Redirect to a page indicating subscription is required
                messages.add_message(
                        request,
                        messages.INFO,
                        'You need to enroll for this course first!, you can do this for *free* by clicking the enroll button.',
                        extra_tags='alert-warning top_homepage'
                    )
                return HttpResponseRedirect(reverse('content:marketcourse', args=[course.id]))
        else:
            # Redirect to login page if user is not authenticated
            return HttpResponseRedirect(reverse('user:login'))
    return dispatch


class AuthorRequiredMixin:
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            stripe_customer_checks(request.user)
            # Assuming you have a subscription model named Subscription
            if request.user.author_permissions:
                return super().dispatch(request, *args, **kwargs)
            else:
                # Redirect to a page indicating subscription is required
                messages.add_message(
                        request,
                        messages.INFO,
                        'You need to be an approved author, please contact us to request access.',
                        extra_tags='alert-warning top_homepage'
                    )
                return HttpResponseRedirect(reverse('main:index'))
        else:
            # Redirect to login page if user is not authenticated
            return HttpResponseRedirect(reverse('user:login'))


def AuthorRequiredDec(f):
    @wraps(f)
    def dispatch(request, *args, **kwargs):
        if request.user.is_authenticated:
            stripe_customer_checks(request.user)
            if request.user.author_permissions:
                return f(request, *args, **kwargs)
            else:
                messages.add_message(
                    request,
                    messages.INFO,
                    'You need to be an approved author, please contact us to request access.',
                    extra_tags='alert-warning top_homepage'
                )
                return HttpResponseRedirect(reverse('main:index'))
        else:
            return HttpResponseRedirect(reverse('user:login'))
    return dispatch


class AffiliateRequiredMixin:
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            stripe_customer_checks(request.user)
            # Assuming you have a subscription model named Subscription
            if request.user.affiliate_permissions:
                return super().dispatch(request, *args, **kwargs)
            else:
                # Redirect to a page indicating subscription is required
                messages.add_message(
                        request,
                        messages.INFO,
                        'You need to be an approved, please contact us to request access.',
                        extra_tags='alert-warning top_homepage'
                    )
                return HttpResponseRedirect(reverse('main:index'))
        else:
            # Redirect to login page if user is not authenticated
            return HttpResponseRedirect(reverse('user:login'))


def AffiliateRequiredDec(f):
    @wraps(f)
    def dispatch(request, *args, **kwargs):
        if request.user.is_authenticated:
            stripe_customer_checks(request.user)
            if request.user.affiliate_permissions:
                return f(request, *args, **kwargs)
            else:
                messages.add_message(
                    request,
                    messages.INFO,
                    'You need to be an approved affiliate, please contact us to request access.',
                    extra_tags='alert-warning top_homepage'
                )
                return HttpResponseRedirect(reverse('main:index'))
        else:
            return HttpResponseRedirect(reverse('user:login'))
    return dispatch


class TrusteeRequiredMixin:
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            stripe_customer_checks(request.user)
            # Assuming you have a subscription model named Subscription
            if request.user.affiliate_permissions or request.user.author_permissions:
                return super().dispatch(request, *args, **kwargs)
            else:
                # Redirect to a page indicating subscription is required
                messages.add_message(
                        request,
                        messages.INFO,
                        'You need to be an approved author or affiliate, please contact us to request access.',
                        extra_tags='alert-warning top_homepage'
                    )
                return HttpResponseRedirect(reverse('main:index'))
        else:
            # Redirect to login page if user is not authenticated
            return HttpResponseRedirect(reverse('user:login'))


def TrusteeRequiredDec(f):
    @wraps(f)
    def dispatch(request, *args, **kwargs):
        if request.user.is_authenticated:
            stripe_customer_checks(request.user)
            if request.user.affiliate_permissions or request.user.author_permissions:
                return f(request, *args, **kwargs)
            else:
                messages.add_message(
                    request,
                    messages.INFO,
                    'You need to be an approved author or affiliate, please contact us to request access.',
                    extra_tags='alert-warning top_homepage'
                )
                return HttpResponseRedirect(reverse('main:index'))
        else:
            return HttpResponseRedirect(reverse('user:login'))
    return dispatch
