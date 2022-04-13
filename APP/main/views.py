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
