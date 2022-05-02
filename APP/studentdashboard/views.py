from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.views import generic
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.utils.functional import cached_property
from view_breadcrumbs import BaseBreadcrumbMixin

# Create your views here.







class IndexView(BaseBreadcrumbMixin, generic.ListView):
    template_name = "studentdashboard/index.html"
    context_object_name = 'context'
    @cached_property
    def crumbs(self):
        return [
                ("dashboard", reverse("studentdashboard:index")),
                ("main", reverse("studentdashboard:index"))
                ]
    def get_queryset(self):
        return "user_index"








class ButtonsView(BaseBreadcrumbMixin, generic.ListView):
    template_name = "studentdashboard/buttons.html"
    context_object_name = 'context'
    @cached_property
    def crumbs(self):
        return [
                ("dashboard", reverse("studentdashboard:index")),
                ("buttons", reverse("studentdashboard:buttons"))
                ]
    def get_queryset(self):
        return "user_index"








class CardsView(BaseBreadcrumbMixin,generic.ListView):
    template_name = "studentdashboard/cards.html"
    context_object_name = 'context'
    @cached_property
    def crumbs(self):
        return [
                ("dashboard", reverse("studentdashboard:index")),
                ("cards", reverse("studentdashboard:cards"))
                ]
    def get_queryset(self):
        return "user_index"








class UtilColorView(BaseBreadcrumbMixin, generic.ListView):
    template_name = "s-dash-utilities/utilities-color.html"
    context_object_name = 'context'
    @cached_property
    def crumbs(self):
        return [
                ("dashboard", reverse("studentdashboard:index")),
                ("color", reverse("studentdashboard:util-color"))
                ]
    def get_queryset(self):
        return "user_index"








class UtilBorderView(BaseBreadcrumbMixin, generic.ListView):
    template_name = "s-dash-utilities/utilities-border.html"
    context_object_name = 'context'
    @cached_property
    def crumbs(self):
        return [
                ("dashboard", reverse("studentdashboard:index")),
                ("border", reverse("studentdashboard:util-border"))
                ]
    def get_queryset(self):
        return "user_index"








class UtilAnimationView(BaseBreadcrumbMixin, generic.ListView):
    template_name = "s-dash-utilities/utilities-animation.html"
    context_object_name = 'context'
    @cached_property
    def crumbs(self):
        return [
                ("dashboard", reverse("studentdashboard:index")),
                ("animation", reverse("studentdashboard:util-animation"))
                ]
    def get_queryset(self):
        return "user_index"








class UtilOtherView(BaseBreadcrumbMixin, generic.ListView):
    template_name = "s-dash-utilities/utilities-other.html"
    context_object_name = 'context'
    @cached_property
    def crumbs(self):
        return [
                ("dashboard", reverse("studentdashboard:index")),
                ("other", reverse("studentdashboard:util-other"))
                ]
    def get_queryset(self):
        return "user_index"








class BlankView(BaseBreadcrumbMixin, generic.ListView):
    template_name = "studentdashboard/blank.html"
    context_object_name = 'context'
    @cached_property
    def crumbs(self):
        return [
                ("dashboard", reverse("studentdashboard:index")),
                ("blank", reverse("studentdashboard:blank"))
                ]
    def get_queryset(self):
        return "user_index"








class ChartsView(BaseBreadcrumbMixin, generic.ListView):
    template_name = "studentdashboard/charts.html"
    context_object_name = 'context'
    @cached_property
    def crumbs(self):
        return [
                ("dashboard", reverse("studentdashboard:index")),
                ("charts", reverse("studentdashboard:charts"))
                ]
    def get_queryset(self):
        return "user_index"








class TablesView(BaseBreadcrumbMixin, generic.ListView):
    template_name = "studentdashboard/tables.html"
    context_object_name = 'context'
    @cached_property
    def crumbs(self):
        return [
                ("dashboard", reverse("studentdashboard:index")),
                ("tables", reverse("studentdashboard:tables"))
                ]
    def get_queryset(self):
        return "user_index"








class NotFoundView(BaseBreadcrumbMixin, generic.ListView):
    template_name = "studentdashboard/404.html"
    context_object_name = 'context'
    @cached_property
    def crumbs(self):
        return [
                ("dashboard", reverse("studentdashboard:index")),
                ("404", reverse("studentdashboard:404"))
                ]
    def get_queryset(self):
        return "user_index"
