from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.views import generic
from .util.ContentSync import QuestionSync,PointSync,VideoSync,SpecificationSync
from .util.ContentCRUD import QuestionCRUD,PointCRUD,SpecificationCRUD
#
from .models import *
# Create your views here.

class IndexView(generic.ListView):
    template_name = 'content/index.html'
    context_object_name = 'context'
    def get_queryset(self):
        """Return the last three published questions."""
        return 'content_index'

class ContentView(generic.ListView):
    template_name = 'content/content.html'
    context_object_name = 'context'
    def get_queryset(self):
        """Return all of the required hub information"""
        return 'content_content'


class HubView(generic.ListView):
    template_name = 'content/hub.html'
    context_object_name = 'context'
    def get_queryset(self):
        """Return all of the required hub information"""
        return 'content_hub'

class StatisticsView(generic.ListView):
    template_name = 'content/statistics.html'
    context_object_name = 'context'
    def get_queryset(self):
        """Return all of the required hub information"""
        return 'content_statistics'











