from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.views import generic
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.utils.functional import cached_property
from view_breadcrumbs import BaseBreadcrumbMixin
from django.contrib.auth.mixins import LoginRequiredMixin


# Create your views here.
class IndexView(LoginRequiredMixin, BaseBreadcrumbMixin, generic.ListView):
    login_url = 'user:login'
    redirect_field_name = None
    template_name = "dashboard/index.html"
    context_object_name = 'context'

    @cached_property
    def crumbs(self):
        return [
                ("dashboard", reverse("dashboard:index")),
                ("Home", reverse("dashboard:index"))
                ]

    def get_queryset(self):
        context = {}
        context['sidebar_active'] = 'dashboard/index'
        return context


# Admin views
class AdminTrafficView(
            LoginRequiredMixin, BaseBreadcrumbMixin, generic.ListView
        ):
    login_url = 'user:login'
    redirect_field_name = None
    template_name = "dashboard/admin/traffic.html"
    context_object_name = 'context'

    @cached_property
    def crumbs(self):
        return [
                ("dashboard", reverse("dashboard:index")),
                ("traffic", reverse("dashboard:admin_traffic"))
                ]

    def get_queryset(self):
        context = {}
        context['sidebar_active'] = 'admin/traffic'
        return context


class StudentPerformanceView(
            LoginRequiredMixin, BaseBreadcrumbMixin, generic.ListView
        ):
    login_url = 'user:login'
    redirect_field_name = None
    template_name = "dashboard/student/performance.html"
    context_object_name = 'context'

    @cached_property
    def crumbs(self):
        return [
                ("dashboard", reverse("dashboard:index")),
                ("perfromance", reverse("dashboard:student_performance"))
                ]

    def get_queryset(self):
        context = {}
        context['sidebar_active'] = 'student/performance'
        return context


class TeacherClassesView(
            LoginRequiredMixin, BaseBreadcrumbMixin, generic.ListView
        ):
    login_url = 'user:login'
    redirect_field_name = None
    template_name = "dashboard/teacher/classes.html"
    context_object_name = 'context'

    @cached_property
    def crumbs(self):
        return [
                ("dashboard", reverse("dashboard:index")),
                ("classes", reverse("dashboard:teacher_classes"))
                ]

    def get_queryset(self):
        context = {}
        context['sidebar_active'] = 'teacher/classes'
        return context


class TutorClassesView(
            LoginRequiredMixin, BaseBreadcrumbMixin, generic.ListView
        ):
    login_url = 'user:login'
    redirect_field_name = None
    template_name = "dashboard/tutor/classes.html"
    context_object_name = 'context'

    @cached_property
    def crumbs(self):
        return [
                ("dashboard", reverse("dashboard:index")),
                ("classes", reverse("dashboard:tutor_classes"))
                ]

    def get_queryset(self):
        context = {}
        context['sidebar_active'] = 'tutor/classes'
        return context


class SchoolManagementView(
            LoginRequiredMixin, BaseBreadcrumbMixin, generic.ListView
        ):
    login_url = 'user:login'
    redirect_field_name = None
    template_name = "dashboard/school/management.html"
    context_object_name = 'context'

    @cached_property
    def crumbs(self):
        return [
                ("dashboard", reverse("dashboard:index")),
                ("management", reverse("dashboard:school_management"))
                ]

    def get_queryset(self):
        context = {}
        context['sidebar_active'] = 'school/management'
        return context


class CenterManagementView(
            LoginRequiredMixin, BaseBreadcrumbMixin, generic.ListView
        ):
    login_url = 'user:login'
    redirect_field_name = None
    template_name = "dashboard/center/management.html"
    context_object_name = 'context'

    @cached_property
    def crumbs(self):
        return [
                ("dashboard", reverse("dashboard:index")),
                ("management", reverse("dashboard:center_management"))
                ]

    def get_queryset(self):
        context = {}
        context['sidebar_active'] = 'center/management'
        return context


class EditorTasksView(
            LoginRequiredMixin, BaseBreadcrumbMixin, generic.ListView
        ):
    login_url = 'user:login'
    redirect_field_name = None
    template_name = "dashboard/editor/tasks.html"
    context_object_name = 'context'

    @cached_property
    def crumbs(self):
        return [
                ("dashboard", reverse("dashboard:index")),
                ("tasks", reverse("dashboard:editor_tasks"))
                ]

    def get_queryset(self):
        context = {}
        context['sidebar_active'] = 'editor/tasks'
        return context


class AffiliateStatisticsView(
            LoginRequiredMixin, BaseBreadcrumbMixin, generic.ListView
        ):
    login_url = 'user:login'
    redirect_field_name = None
    template_name = "dashboard/affiliate/statistics.html"
    context_object_name = 'context'

    @cached_property
    def crumbs(self):
        return [
                ("dashboard", reverse("dashboard:index")),
                ("statistics", reverse("dashboard:affiliate_statistics"))
                ]

    def get_queryset(self):
        context = {}
        context['sidebar_active'] = 'affiliate/statistics'
        return context


class BlankView(LoginRequiredMixin, BaseBreadcrumbMixin, generic.ListView):
    login_url = 'user:login'
    redirect_field_name = None
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


class NotFoundView(LoginRequiredMixin, BaseBreadcrumbMixin, generic.ListView):
    login_url = 'user:login'
    redirect_field_name = None
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
