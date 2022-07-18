from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.views import generic
from django.utils.functional import cached_property
from view_breadcrumbs import BaseBreadcrumbMixin
from django.core.mail import send_mail

# Create your views here.





class IndexView(BaseBreadcrumbMixin,generic.ListView):
    template_name = "main/index.html"
    context_object_name = 'context'
    @cached_property
    def crumbs(self):
        return [
                ("home", reverse("main:index"))
                ]
    def get_queryset(self):
        return "base_index"
  








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








class SiteMapSEOView(BaseBreadcrumbMixin, generic.ListView):
    template_name = "main/sitemapseo.html"
    context_object_name = 'context'
    @cached_property
    def crumbs(self):
        return [
                ("sitemapseo", reverse("main:sitemapseo"))
                ]
    def get_queryset(self):
        return "base_sitemap_seo"







