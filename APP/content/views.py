from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.utils.functional import cached_property
from django.views import generic
from content.util.ContentSync import QuestionSync,PointSync,VideoSync,SpecificationSync
from content.util.ContentCRUD import QuestionCRUD,PointCRUD,SpecificationCRUD
from view_breadcrumbs import BaseBreadcrumbMixin

#
from content.models import *

# Create your views here.













class IndexView(BaseBreadcrumbMixin,generic.TemplateView):
    template_name = 'content/index.html'
    context_object_name = 'context'

    @cached_property
    def crumbs(self):
        return [
                ("my", reverse("content:index"))
                ]
    def get_queryset(self):
        """Return the last three published questions."""
        return 'content_index'









class ContentView(BaseBreadcrumbMixin,generic.ListView):
    template_name = 'content/content.html'
    context_object_name = 'context'

    @cached_property
    def crumbs(self):
        return [
                ("my", reverse("content:index")),
                ("content", reverse("content:content"))
                ]
    def get_queryset(self):
        """Return all of the required hub information"""
        return 'content_content'










class HubView(BaseBreadcrumbMixin,generic.ListView):
    template_name = 'content/hub.html'
    context_object_name = 'context'
    @cached_property
    def crumbs(self):
        return [
                ("my", reverse("content:index")),
                ("hub", reverse("content:hub"))
                ]
    def get_queryset(self):
        """Return all of the required hub information"""
        return 'content_hub'









class StatisticsView(BaseBreadcrumbMixin,generic.ListView):
    template_name = 'content/statistics.html'
    context_object_name = 'context'
    @cached_property
    def crumbs(self):
        return [
                ("my", reverse("content:index")),
                ("statistics", reverse("content:statistics"))
                ]
    def get_queryset(self):
        """Return all of the required hub information"""
        return 'content_statistics'










class QuestionsView(BaseBreadcrumbMixin,generic.ListView):
    template_name = 'content/questions.html'
    context_object_name = 'context'
    @cached_property
    def crumbs(self):
        return [
                ("my", reverse("content:index")),
                ("content", reverse("content:content")),
                ("questions", reverse("content:questions"))
                ]
    def get_queryset(self):
        """Return all of the required hub information"""
        return 'content_questions'








class QuestionView(BaseBreadcrumbMixin,generic.ListView):
    template_name = 'content/question.html'
    context_object_name = 'context'
    @cached_property
    def crumbs(self):
        return [
                ("my", reverse("content:index")),
                ("content", reverse("content:content")),
                ("questions", reverse("content:questions")),
                ("question", reverse("content:question"))
                ]
    def get_queryset(self):
        """Return all of the required hub information"""
        return 'content_questions'








class NotesView(BaseBreadcrumbMixin,generic.ListView):
    template_name = 'content/notes.html'
    context_object_name = 'context'
    @cached_property
    def crumbs(self):
        return [
                ("my", reverse("content:index")),
                ("content", reverse("content:content")),
                ("notes", reverse("content:notes")),
                ]
    def get_queryset(self):
        """Return all of the required hub information"""
        return 'content_notes'








class PaperView(BaseBreadcrumbMixin,generic.ListView):
    template_name = 'content/paper.html'
    context_object_name = 'context'
    @cached_property
    def crumbs(self):
        return [
                ("my", reverse("content:index")),
                ("content", reverse("content:content")),
                ("paper", reverse("content:paper")),
                ]
    def get_queryset(self):
        """Return all of the required hub information"""
        return 'content_paper'








class UserPaperView(BaseBreadcrumbMixin,generic.ListView):
    template_name = 'content/user-paper.html'
    context_object_name = 'context'
    @cached_property
    def crumbs(self):
        return [
                ("my", reverse("content:index")),
                ("content", reverse("content:content")),
                ("user-paper", reverse("content:user-paper")),
                ]
    def get_queryset(self):
        """Return all of the required hub information"""
        return 'content_user_paper'








class UserPaperPrintView(BaseBreadcrumbMixin,generic.ListView):
    template_name = 'content/user-paper-print.html'
    context_object_name = 'context'
    @cached_property
    def crumbs(self):
        return [
                ("my", reverse("content:index")),
                ("content", reverse("content:content")),
                ("user-paper", reverse("content:user-paper")),
                ("print", reverse("content:user-paper-print")),
                ]
    def get_queryset(self):
        """Return all of the required hub information"""
        return 'content_user_paper-print'









