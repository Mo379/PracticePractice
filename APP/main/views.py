from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.views import generic

# Create your views here.
class IndexView(generic.ListView):
    template_name = "main/index.html"
    context_object_name = 'context'
    def get_queryset(self):
        return "base_index"
class AboutView(generic.ListView):
    template_name = "main/about.html"
    context_object_name = 'context'
    def get_queryset(self):
        return "base_about"
class ReviewView(generic.ListView):
    template_name = "main/review.html"
    context_object_name = 'context'
    def get_queryset(self):
        return "base_review"
class ContactView(generic.ListView):
    template_name = "main/contact.html"
    context_object_name = 'context'
    def get_queryset(self):
        return "base_contact"
class JobsView(generic.ListView):
    template_name = "main/jobs.html"
    context_object_name = 'context'
    def get_queryset(self):
        return "base_jobs"
class FAQView(generic.ListView):
    template_name = "main/faq.html"
    context_object_name = 'context'
    def get_queryset(self):
        return "base_faq"
class TermsAndConditionsView(generic.ListView):
    template_name = "main/tandc.html"
    context_object_name = 'context'
    def get_queryset(self):
        context = {
                "CompanyName":"PracticePractice",
                "SiteURL":"practicepractice.net",
                "CompanyNumber":"12679239",
                "InfoContact":"Info@practicepractice.com",
                "TeamContact":"Contact@practicepractice.com",
                }
        return context
class PrivacyView(generic.ListView):
    template_name = "main/privacy.html"
    context_object_name = 'context'
    def get_queryset(self):
        context = {
                "CompanyName":"PracticePractice",
                "CompanyNumber":"12679239",
                "InfoContact":"Info@practicepractice.com",
                "TeamContact":"Contact@practicepractice.com",
                }
        return context
class SiteMapView(generic.ListView):
    template_name = "main/sitemap.html"
    context_object_name = 'context'
    def get_queryset(self):
        return "base_sitemap"
class SiteMapSEOView(generic.ListView):
    template_name = "main/sitemapseo.html"
    context_object_name = 'context'
    def get_queryset(self):
        return "base_sitemap_seo"
