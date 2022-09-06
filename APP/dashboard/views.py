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
    template_name = "dashboard/index.html"
    context_object_name = 'context'
    @cached_property
    def crumbs(self):
        return [
                ("dashboard", reverse("dashboard:index")),
                ("main", reverse("dashboard:index"))
                ]
    def get_queryset(self):
        return "user_index"








class ButtonsView(BaseBreadcrumbMixin, generic.ListView):
    template_name = "dashboard/buttons.html"
    context_object_name = 'context'
    @cached_property
    def crumbs(self):
        return [
                ("dashboard", reverse("dashboard:index")),
                ("buttons", reverse("dashboard:buttons"))
                ]
    def get_queryset(self):
        return "user_index"








class CardsView(BaseBreadcrumbMixin,generic.ListView):
    template_name = "dashboard/cards.html"
    context_object_name = 'context'
    @cached_property
    def crumbs(self):
        return [
                ("dashboard", reverse("dashboard:index")),
                ("cards", reverse("dashboard:cards"))
                ]
    def get_queryset(self):
        return "user_index"








class UtilColorView(BaseBreadcrumbMixin, generic.ListView):
    template_name = "dashboard/utilities/utilities-color.html"
    context_object_name = 'context'
    @cached_property
    def crumbs(self):
        return [
                ("dashboard", reverse("dashboard:index")),
                ("color", reverse("dashboard:util-color"))
                ]
    def get_queryset(self):
        return "user_index"








class UtilBorderView(BaseBreadcrumbMixin, generic.ListView):
    template_name = "dashboard/utilities/utilities-border.html"
    context_object_name = 'context'
    @cached_property
    def crumbs(self):
        return [
                ("dashboard", reverse("dashboard:index")),
                ("border", reverse("dashboard:util-border"))
                ]
    def get_queryset(self):
        return "user_index"








class UtilAnimationView(BaseBreadcrumbMixin, generic.ListView):
    template_name = "dashboard/utilities/utilities-animation.html"
    context_object_name = 'context'
    @cached_property
    def crumbs(self):
        return [
                ("dashboard", reverse("dashboard:index")),
                ("animation", reverse("dashboard:util-animation"))
                ]
    def get_queryset(self):
        return "user_index"








class UtilOtherView(BaseBreadcrumbMixin, generic.ListView):
    template_name = "dashboard/utilities/utilities-other.html"
    context_object_name = 'context'
    @cached_property
    def crumbs(self):
        return [
                ("dashboard", reverse("dashboard:index")),
                ("other", reverse("dashboard:util-other"))
                ]
    def get_queryset(self):
        return "user_index"








class BlankView(BaseBreadcrumbMixin, generic.ListView):
    template_name = "dashboard/blank.html"
    context_object_name = 'context'
    @cached_property
    def crumbs(self):
        return [
                ("dashboard", reverse("dashboard:index")),
                ("blank", reverse("dashboard:blank"))
                ]
    def get_queryset(self):
        return "user_index"








class ChartsView(BaseBreadcrumbMixin, generic.ListView):
    template_name = "dashboard/charts.html"
    context_object_name = 'context'
    @cached_property
    def crumbs(self):
        return [
                ("dashboard", reverse("dashboard:index")),
                ("charts", reverse("dashboard:charts"))
                ]
    def get_queryset(self):
        return "user_index"








class TablesView(BaseBreadcrumbMixin, generic.ListView):
    template_name = "dashboard/tables.html"
    context_object_name = 'context'
    @cached_property
    def crumbs(self):
        return [
                ("dashboard", reverse("dashboard:index")),
                ("tables", reverse("dashboard:tables"))
                ]
    def get_queryset(self):
        return "user_index"








class NotFoundView(BaseBreadcrumbMixin, generic.ListView):
    template_name = "dashboard/404.html"
    context_object_name = 'context'
    @cached_property
    def crumbs(self):
        return [
                ("dashboard", reverse("dashboard:index")),
                ("404", reverse("dashboard:404"))
                ]
    def get_queryset(self):
        return "user_index"
