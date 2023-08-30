from functools import wraps
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib import messages
from djstripe.models import (
        Customer,
        Subscription,
        Price,
    )
from content.models import Course, CourseSubscription


class AnySubscriptionRequiredMixin:
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            # Assuming you have a subscription model named Subscription
            admin_customer = Customer.objects.get(id=request.user.id)
            if Subscription.objects.filter(customer=admin_customer, status='active').exists():
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
            # Assuming you have a subscription model named Subscription
            admin_customer = Customer.objects.get(id=request.user.id)
            if Subscription.objects.filter(customer=admin_customer, status='active').exists():
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
            # Assuming you have a subscription model named Subscription
            admin_customer = Customer.objects.get(id=request.user.id)
            active_subscriptions = Subscription.objects.filter(customer=admin_customer, status='active')
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
            admin_customer = Customer.objects.get(id=request.user.id)
            active_subscriptions = Subscription.objects.filter(customer=admin_customer, status='active')
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
            # Assuming you have a subscription model named Subscription
            course = Course.objects.get(pk=kwargs['course_id'])
            if CourseSubscription.objects.filter(user=request.user, course=course).exists:
                return super().dispatch(request, *args, **kwargs)
            else:
                # Redirect to a page indicating subscription is required
                messages.add_message(
                        request,
                        messages.INFO,
                        'You need to enroll for this course first!',
                        extra_tags='alert-warning top_homepage'
                    )
                return HttpResponseRedirect(reverse('marketcourse', args=[course.id]))
        else:
            # Redirect to login page if user is not authenticated
            return HttpResponseRedirect(reverse('user:login'))


class AuthorRequiredMixin:
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
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
