import requests
import stripe
from django.http import HttpResponse, HttpResponseRedirect
from django.conf import settings
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.views import generic
from django.utils.functional import cached_property
from view_breadcrumbs import BaseBreadcrumbMixin
from django.core.mail import send_mail
from django.contrib import messages
from django.views.decorators.http import require_GET
from djstripe.models import (
        Customer,
        Subscription,
        Price,
    )
from PP2.mixin import (
        AnySubscriptionRequiredMixin,
        AnySubscriptionRequiredDec,
        AISubscriptionRequiredMixin,
        AISubscriptionRequiredDec,
        AuthorRequiredMixin,
        AuthorRequiredDec,
        AffiliateRequiredMixin,
        AffiliateRequiredDec,
        TrusteeRequiredMixin,
        TrusteeRequiredDec
    )




# Create your views here.
class IndexView(BaseBreadcrumbMixin, generic.ListView):
    template_name = "main/index.html"
    context_object_name = 'context'

    @cached_property
    def crumbs(self):
        return [
                ("home", reverse("main:index"))
                ]


    def get_queryset(self):
        #messages.add_message(
        #        self.request,
        #        messages.INFO,
        #        'This is the top of the home page',
        #        extra_tags='alert-danger top_homepage'
        #    )
        context = {}
        user = self.request.user
        if user.is_authenticated:
            try:
                Customer.objects.get(id=user.id)
            except:
                stripe.api_key = settings.STRIPE_SECRET_KEY
                stripe.Customer.create(
                        email=user.email,
                        name=user.first_name+' '+user.last_name,
                        id=user.id,
                        metadata={'username':user.username}
                    )
            #
            if Subscription.objects.filter(customer=user.id, status__in=['active','trialing']).exists() is False:
                auth_key = settings.STRIPE_SECRET_KEY
                url = "https://api.stripe.com/v1/customer_sessions"
                data = {
                    "customer": user.id
                }

                headers = {
                    "Authorization": f"Bearer {auth_key}",
                }

                response = requests.post(url, data=data, headers=headers)
                client_secret = response.json()['client_secret']

                context['client_secret'] = client_secret
                context['user_is_subscribed'] = False
            else:
                context['client_secret'] = None
                context['user_is_subscribed'] = True
        #
        context['publishable_key'] = settings.STRIPE_PUBLISHABLE_KEY
        context['without_ai_monthly_plan'] = Price.objects.get(id='price_1Nf0s1CUEyV7FMWeH5sz68Hw')
        context['without_ai_threemonth_plan'] = Price.objects.get(id='price_1Nf0s1CUEyV7FMWe0YJ1jXNX')
        context['without_ai_sixmonth_plan'] = Price.objects.get(id='price_1Nf0s1CUEyV7FMWeqSyB5D8T')
        #
        context['with_ai_monthly_plan'] = Price.objects.get(id='price_1Nf0oUCUEyV7FMWeLnm8V1EC')
        context['with_ai_threemonth_plan'] = Price.objects.get(id='price_1Nf0oUCUEyV7FMWeKLYogkM2')
        context['with_ai_sixmonth_plan'] = Price.objects.get(id='price_1Nf0oUCUEyV7FMWeUr0fHRaW')
        return context








class AboutView(BaseBreadcrumbMixin ,generic.ListView):
    template_name = "main/about.html"
    context_object_name = 'context'
    @cached_property
    def crumbs(self):
        return [
                ("about", reverse("main:about"))
                ]
    def get_queryset(self):
        return "base_about"








class ReviewView(BaseBreadcrumbMixin ,generic.ListView):
    template_name = "main/review.html"
    context_object_name = 'context'
    @cached_property
    def crumbs(self):
        return [
                ("reviews", reverse("main:review"))
                ]
    def get_queryset(self):
        return "base_review"








class ContactView(BaseBreadcrumbMixin, generic.ListView):
    template_name = "main/contact.html"
    context_object_name = 'context'
    @cached_property
    def crumbs(self):
        return [
                ("contact", reverse("main:contact"))
                ]
    def get_queryset(self):
        return "base_contact"








class JobsView(BaseBreadcrumbMixin, generic.ListView):
    template_name = "main/jobs.html"
    context_object_name = 'context'
    @cached_property
    def crumbs(self):
        return [
                ("jobs", reverse("main:jobs"))
                ]
    def get_queryset(self):
        return "base_jobs"








class FAQView(BaseBreadcrumbMixin, generic.ListView):
    template_name = "main/faq.html"
    context_object_name = 'context'
    @cached_property
    def crumbs(self):
        return [
                ("faqs", reverse("main:faq"))
                ]
    def get_queryset(self):
        return "base_faq"








class TermsAndConditionsView(BaseBreadcrumbMixin, generic.ListView):
    template_name = "main/tandc.html"
    context_object_name = 'context'
    @cached_property
    def crumbs(self):
        return [
                ("terms", reverse("main:tandc"))
                ]
    def get_queryset(self):
        context = {
                "CompanyName":"PracticePractice",
                "SiteURL":"practicepractice.net",
                "CompanyNumber":"12679239",
                "InfoContact":"Info@practicepractice.com",
                "TeamContact":"Contact@practicepractice.com",
                }
        return context








class PrivacyView(BaseBreadcrumbMixin, generic.ListView):
    template_name = "main/privacy.html"
    context_object_name = 'context'
    @cached_property
    def crumbs(self):
        return [
                ("privacy", reverse("main:privacy"))
                ]
    def get_queryset(self):
        context = {
                "CompanyName":"PracticePractice",
                "CompanyNumber":"12679239",
                "InfoContact":"Info@practicepractice.com",
                "TeamContact":"Contact@practicepractice.com",
                }
        return context


class SiteMapView(BaseBreadcrumbMixin, generic.ListView):
    template_name = "main/sitemap.html"
    context_object_name = 'context'
    @cached_property
    def crumbs(self):
        return [
                ("sitemap", reverse("main:sitemap"))
                ]
    def get_queryset(self):
        return "base_sitemap"


class NotFoundView(BaseBreadcrumbMixin, generic.ListView):
    template_name = "main/404.html"
    context_object_name = 'context'

    @cached_property
    def crumbs(self):
        return [
                ("Home", reverse("main:index")),
                ("404", '')
                ]
    def get(self, request, *args, **kwargs):
        response = super(generic.ListView, self).get(request, *args, **kwargs)
        response.status_code = 404
        return response

    def get_queryset(self):
        return "user_index"


class ErrorView(BaseBreadcrumbMixin, generic.ListView):
    template_name = "main/500.html"
    context_object_name = 'context'

    @cached_property
    def crumbs(self):
        return [
                ("Home", reverse("main:index")),
                ("500", '')
                ]

    def get(self, request, *args, **kwargs):
        response = super(generic.ListView, self).get(request, *args, **kwargs)
        response.status_code = 500
        return response

    def get_queryset(self):
        return "user_index"


@require_GET
def robots_txt(request):
    lines = [
        "User-Agent: *",
        "Disallow: /user/",
        "Disallow: /_*/",
        "Sitemap: https://www.practicepractice.net/sitemap.xml",
    ]
    return HttpResponse("\n".join(lines), content_type="text/plain")
