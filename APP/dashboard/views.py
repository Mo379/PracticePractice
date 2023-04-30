import collections
import pandas as pd
from django.conf import settings
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.views import generic
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.utils.functional import cached_property
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from view_breadcrumbs import BaseBreadcrumbMixin
from django.db.models import CharField
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank
from braces.views import (
        LoginRequiredMixin,
        GroupRequiredMixin,
        SuperuserRequiredMixin,
    )
from content.models import (
        Question,
        Point,
        Specification,
        Collaborator,
        ContributionTask,
        Contribution,
        Course,
        CourseVersion,
        CourseSubscription,
        CourseReview
    )
from content.util.GeneralUtil import (
        filter_drag_drop_selection,
        order_full_spec_content,
        order_live_spec_content
    )



# Superuser views
class SuperuserMonitorView(
            LoginRequiredMixin,
            SuperuserRequiredMixin,
            BaseBreadcrumbMixin,
            generic.ListView
        ):
    login_url = 'user:login'
    redirect_field_name = False
    template_name = "dashboard/superuser/monitor.html"
    context_object_name = 'context'

    @cached_property
    def crumbs(self):
        return [
                ("dashboard", reverse("dashboard:index")),
                ]

    def get_queryset(self):
        context = {}
        context['sidebar_active'] = 'superuser/monitor'
        return context


class IndexView(
            BaseBreadcrumbMixin,
            generic.ListView
        ):

    template_name = "dashboard/general/index.html"
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


class MarketPlaceView(
            BaseBreadcrumbMixin,
            generic.ListView
        ):

    template_name = "dashboard/general/marketplace.html"
    context_object_name = 'context'

    @cached_property
    def crumbs(self):
        return [
                ("dashboard", reverse("dashboard:index")),
                ("MarketPlace", '')
                ]

    def get_queryset(self):
        context = {}
        current_page = self.kwargs['page'] if 'page' in self.kwargs else 1
        context['sidebar_active'] = 'dashboard/marketplace'
        courses = Course.objects.filter(
                course_publication=True,
                deleted=False
                )
        #
        if 'search' in self.request.GET:
            search_query = self.request.GET['search']
            vector = SearchVector('course_name')
            query = SearchQuery(search_query)
            courses = courses.annotate(
                    rank=SearchRank(vector, query)
                ).order_by('-rank')
        p = Paginator(courses, 9)
        try:
            context['courses'] = p.page(current_page)
        except EmptyPage:
            context['courses'] = p.page(p.num_pages)
            current_page = p.num_pages
        context['num_pages'] = p.num_pages
        context['current_page'] = current_page
        context['previous_page'] = current_page - 1 if current_page > 1 else None
        context['next_page'] = current_page + 1 if current_page < p.num_pages else None
        context['CDN_URL'] = settings.CDN_URL
        return context


class MarketCourseView(
            BaseBreadcrumbMixin,
            generic.ListView
        ):

    template_name = "dashboard/general/marketcourse.html"
    context_object_name = 'context'

    @cached_property
    def crumbs(self):
        return [
                ("dashboard", reverse("dashboard:index")),
                ("MarketPlace", reverse("dashboard:marketplace", kwargs={'page':1})),
                ("Course", '')
                ]

    def get_queryset(self):
        context = {}
        context['sidebar_active'] = 'dashboard/marketcourse'
        course_id = self.kwargs['course_id']
        course = Course.objects.get(pk=course_id)
        versions = CourseVersion.objects.filter(course=course).order_by(
                    '-version_number'
                )
        subscription_status = CourseSubscription.objects.filter(
                user=self.request.user,
                course=course
            ).exists() if self.request.user.is_authenticated else False
        content = order_live_spec_content(versions[0].version_content)
        context['course'] = course
        context['versions'] = versions
        context['ordered_content'] = content
        context['course_subscription_status'] = subscription_status
        context['CDN_URL'] = settings.CDN_URL
        return context


class CourseReviewsView(
            BaseBreadcrumbMixin,
            generic.ListView
        ):

    template_name = "dashboard/general/course_reviews.html"
    context_object_name = 'context'

    @cached_property
    def crumbs(self):
        return [
                ("dashboard", reverse("dashboard:index")),
                ("MarketPlace", reverse("dashboard:marketplace")),
                ("Course", reverse("dashboard:marketcourse", kwargs={'course_id':self.kwargs['course_id']})),
                ("Reviews", '')
                ]

    def get_queryset(self):
        context = {}
        context['sidebar_active'] = 'dashboard/coursereviews'
        course_id = self.kwargs['course_id']
        course = Course.objects.get(pk=course_id)
        reviews = CourseReview.objects.filter(course=course).order_by(
                    '-review_created_at'
                )
        context['course'] = course
        context['reviews'] = reviews
        return context


class StudentPerformanceView(
            LoginRequiredMixin,
            GroupRequiredMixin,
            BaseBreadcrumbMixin,
            generic.ListView
        ):
    login_url = 'user:login'
    redirect_field_name = False
    group_required = u"Student"
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


class StudentContentManagementView(
            LoginRequiredMixin,
            GroupRequiredMixin,
            BaseBreadcrumbMixin,
            generic.ListView
        ):
    login_url = 'user:login'
    redirect_field_name = False
    group_required = u"Student"
    template_name = "dashboard/student/contentmanagement.html"
    context_object_name = 'context'

    @cached_property
    def crumbs(self):
        return [
                ("dashboard", reverse("dashboard:index")),
                ("content management", reverse("dashboard:student_contentmanagement"))
                ]
    def get_queryset(self):
        context = {}
        context['sidebar_active'] = 'student/contentmanagement'
        current_page = self.kwargs['page'] if 'page' in self.kwargs else 1
        course_subscriptions = CourseSubscription.objects.filter(
                user=self.request.user
            ).order_by('-subscription_created_at') if self.request.user.is_authenticated else False
        #
        courses = [c.course.pk for c in course_subscriptions]
        courses = Course.objects.filter(pk__in=courses)
        if 'search' in self.request.GET:
            search_query = self.request.GET['search']
            vector = SearchVector('course_name')
            query = SearchQuery(search_query)
            courses = courses.annotate(
                    rank=SearchRank(vector, query)
                ).order_by('-rank')
        final_courses = []
        for course in courses:
            subscription = course_subscriptions.get(course=course.id)
            final_courses.append((subscription, course))
        p = Paginator(final_courses, 9)
        try:
            context['courses'] = p.page(current_page)
        except EmptyPage:
            context['courses'] = p.page(p.num_pages)
            current_page = p.num_pages
        context['num_pages'] = p.num_pages
        context['current_page'] = current_page
        context['previous_page'] = current_page - 1 if current_page > 1 else None
        context['next_page'] = current_page + 1 if current_page < p.num_pages else None
        context['CDN_URL'] = settings.CDN_URL
        return context


class MyCoursesView(
            LoginRequiredMixin,
            BaseBreadcrumbMixin,
            generic.ListView
        ):
    login_url = 'user:login'
    redirect_field_name = ''

    template_name = "dashboard/general/mycourses.html"
    context_object_name = 'context'

    @cached_property
    def crumbs(self):
        return [
                ("dashboard", reverse("dashboard:index")),
                ("MyCourses", reverse("dashboard:mycourses"))
                ]

    def get_queryset(self):
        context = {}
        context['sidebar_active'] = 'writer/mycourses'
        current_page = self.kwargs['page'] if 'page' in self.kwargs else 1
        #
        specs = Specification.objects.filter(
                    user=self.request.user,
                    spec_completion=True,
                    deleted=False
                )
        courses = Course.objects.filter(
                    user=self.request.user,
                    deleted=False
                ).order_by(
                        '-course_created_at'
                    )
        if 'search' in self.request.GET:
            search_query = self.request.GET['search']
            vector = SearchVector('course_name')
            query = SearchQuery(search_query)
            courses = courses.annotate(
                    rank=SearchRank(vector, query)
                ).order_by('-rank')
        final_courses = []
        for course in courses:
            courseversions = CourseVersion.objects.filter(course=course).order_by(
                        '-version_number'
                    )
            final_courses.append((courseversions, course))
        p = Paginator(final_courses, 9)
        try:
            context['courses'] = p.page(current_page)
        except EmptyPage:
            context['courses'] = p.page(p.num_pages)
            current_page = p.num_pages
        context['num_pages'] = p.num_pages
        context['current_page'] = current_page
        context['previous_page'] = current_page - 1 if current_page > 1 else None
        context['next_page'] = current_page + 1 if current_page < p.num_pages else None
        context['specs'] = specs
        context['CDN_URL'] = settings.CDN_URL
        return context


# Admin views
class MySpecificationsView(
            LoginRequiredMixin,
            BaseBreadcrumbMixin,
            generic.ListView
        ):
    login_url = 'user:login'
    redirect_field_name = False
    template_name = "dashboard/general/specifications.html"
    context_object_name = 'context'

    @cached_property
    def crumbs(self):
        return [
                ("dashboard", reverse("dashboard:index")),
                ("specifications", reverse("dashboard:specifications"))
                ]

    def get_queryset(self):
        context = {}
        context['sidebar_active'] = 'writer/specifications'
        #
        Notes = Specification.objects.filter(
                    user=self.request.user,
                    deleted=False
                ).values(
                    'spec_level',
                    'spec_subject',
                    'spec_board',
                    'spec_name',
                    'id',
                ).distinct().order_by(
                    'spec_level',
                    'spec_subject',
                    'spec_board',
                    'spec_name',
                )
        Notes_objs = [obj for obj in Notes]
        df = pd.DataFrame(Notes_objs)
        def process_specs(df):
            dic = {}
            raw_specs = []
            if len(Notes_objs) > 0:
                for le, s, m, c, idd in zip(
                        list(df['spec_level']),
                        list(df['spec_subject']),
                        list(df['spec_board']),
                        list(df['spec_name']),
                        list(df['id']),
                        ):
                    if le not in dic:
                        dic[le] = {}
                    if s not in dic[le]:
                        dic[le][s] = {}
                    if m not in dic[le][s]:
                        dic[le][s][m] = []
                    spec = Specification.objects.get(pk=idd)
                    dic[le][s][m].append(spec)
                    raw_specs.append(spec)
            return dic, raw_specs
        spec_dic, spec_raw_specs = process_specs(df)
        #
        context['specifications'] = spec_dic
        context['raw_specs'] = spec_raw_specs
        return context


class SpecModuelHandlerView(
            LoginRequiredMixin,
            BaseBreadcrumbMixin,
            generic.ListView
        ):
    login_url = 'user:login'
    redirect_field_name = False
    template_name = "dashboard/general/specmoduelhandler.html"
    context_object_name = 'context'

    @cached_property
    def crumbs(self):
        return [
                ("dashboard", reverse("dashboard:index")),
                ("specifications", reverse("dashboard:specifications")),
                ("designer", '')
                ]

    def get_queryset(self):
        context = {}
        context['sidebar_active'] = 'dashboard/specifications'
        # get kwargs
        level = self.kwargs['level']
        subject = self.kwargs['subject']
        board = self.kwargs['board']
        name = self.kwargs['name']
        # get spec from db
        spec = Specification.objects.get(
                user=self.request.user,
                spec_level=level,
                spec_subject=subject,
                spec_board=board,
                spec_name=name,
            )
        # get moduels from db
        all_chapters = Point.objects.values(
                    'p_level',
                    'p_subject',
                    'p_moduel',
                    'p_chapter',
                ).distinct().order_by(
                    'p_level',
                    'p_subject',
                    'p_moduel',
                    'p_chapter',
                ).filter(
                        user=self.request.user,
                        p_level=level,
                        p_subject=subject,
                        erased=False,
                )
        chapters = all_chapters.filter(deleted=False, erased=False)
        deleted_chapters = all_chapters.exclude(id__in=chapters.values_list('id'))
        moduels = chapters.values(
                    'p_level',
                    'p_subject',
                    'p_moduel',
                ).distinct().order_by(
                    'p_level',
                    'p_subject',
                    'p_moduel',
                )        # reformat moduels
        deleted_modules = deleted_chapters.values(
                    'p_level',
                    'p_subject',
                    'p_moduel',
                ).distinct().order_by(
                    'p_level',
                    'p_subject',
                    'p_moduel',
                )        # reformat moduels
        # Ordering the modules
        moduels_objs = [obj['p_moduel'] for obj in moduels]
        deleted_objs = [obj['p_moduel'] for obj in deleted_modules]
        ordered_spec = order_live_spec_content(spec.spec_content)
        keys = list(ordered_spec.keys())
        left_over = [mod for mod in moduels_objs if mod not in keys]
        moduels_objs = keys
        #
        module_chapters = collections.defaultdict(list)
        for key in keys:
            module_chapters[key] = list(ordered_spec[key]['content'].keys())
        #
        deleted_module_chapters = collections.defaultdict(list)
        for d_mod in deleted_chapters:
            deleted_module_chapters[d_mod['p_moduel']].append(d_mod['p_chapter'])
        #
        removed_module_chapters = collections.defaultdict(list)
        for mod in keys:
            for chap in chapters.filter(p_moduel=mod):
                if chap['p_chapter'] not in ordered_spec[mod]['content'].keys():
                    removed_module_chapters[mod].append(chap['p_chapter'])
        # Getting removed items
        context['spec'] = spec
        context['full_ord_spec'] = ordered_spec
        #
        context['modules'] = moduels_objs
        context['deleted_moduels'] = deleted_objs
        context['removed_items'] = left_over
        #
        context['module_chapters'] = module_chapters
        context['deleted_module_chapters'] = deleted_module_chapters
        context['removed_module_chapters'] = removed_module_chapters
        return context


class SpecTopicHandlerView(
            LoginRequiredMixin,
            BaseBreadcrumbMixin,
            generic.ListView
        ):
    login_url = 'user:login'
    redirect_field_name = False
    template_name = "dashboard/general/spectopichandler.html"
    context_object_name = 'context'

    @cached_property
    def crumbs(self):
        return [
                ("dashboard", reverse("dashboard:index")),
                ("specifications", reverse("dashboard:specifications")),
                ("designer", '')
                ]

    def get_queryset(self):
        context = {}
        context['sidebar_active'] = 'dashboard/specifications'
        #
        level = self.kwargs['level']
        subject = self.kwargs['subject']
        board = self.kwargs['board']
        name = self.kwargs['name']
        moduel = self.kwargs['module']
        chapter = self.kwargs['chapter']

        spec = Specification.objects.get(
                user=self.request.user,
                spec_level=level,
                spec_subject=subject,
                spec_board=board,
                spec_name=name,
            )
        # get chapter questions
        questions = spec.spec_content[moduel]['content'][chapter]['questions']
        for q_level in questions.keys():
            level_questions = questions[q_level]
            qs = Question.objects.filter(q_unique_id__in=level_questions).order_by('q_number')
            questions[q_level] = qs

        # get moduels from db
        all_points = Point.objects.values(
                    'p_level',
                    'p_subject',
                    'p_moduel',
                    'p_chapter',
                    'p_topic',
                    'p_unique_id',
                ).distinct().order_by(
                    'p_level',
                    'p_subject',
                    'p_moduel',
                    'p_chapter',
                    'p_topic',
                    'p_number',
                ).filter(
                        user=self.request.user,
                        p_level=level,
                        p_subject=subject,
                        p_moduel=moduel,
                        p_chapter=chapter,
                        erased=False,
                )
        points = all_points.filter(deleted=False, erased=False)
        deleted_points = all_points.exclude(id__in=points.values_list('id'))
        topics = points.values(
                    'p_level',
                    'p_subject',
                    'p_moduel',
                    'p_topic',
                ).distinct().order_by(
                    'p_level',
                    'p_subject',
                    'p_moduel',
                    'p_topic',
                )        # reformat moduels
        deleted_topics = deleted_points.values(
                    'p_level',
                    'p_subject',
                    'p_moduel',
                    'p_topic',
                ).distinct().order_by(
                    'p_level',
                    'p_subject',
                    'p_moduel',
                    'p_topic',
                )        # reformat moduels
        # Ordering the modules
        topic_objs = [obj['p_topic'] for obj in topics]
        deleted_objs = [obj['p_topic'] for obj in deleted_topics]
        ordered_spec = order_live_spec_content(spec.spec_content)[moduel]['content'][chapter]['content']
        keys = list(ordered_spec.keys())
        left_over = [topic for topic in topic_objs if topic not in keys]
        topic_objs = keys
        #
        topic_points = collections.defaultdict(list)
        for key in keys:
            topic_points[key] = ordered_spec[key]['content'].keys()
        #
        deleted_topic_points = collections.defaultdict(list)
        for d_points in deleted_points:
            deleted_topic_points[d_points['p_topic']].append(d_points['p_unique_id'])
        #
        removed_topic_points = collections.defaultdict(list)
        for topic in keys:
            for point in points.filter(p_topic=topic):
                if point['p_unique_id'] not in ordered_spec[topic]['content'].keys():
                    removed_topic_points[topic].append(point['p_unique_id'])
        # Getting removed items
        context['spec'] = spec
        context['full_ord_spec'] = ordered_spec
        context['questions'] = questions
        #
        context['module'] = moduel
        context['chapter'] = chapter
        #
        context['topics'] = topic_objs
        context['deleted_topics'] = deleted_objs
        context['removed_items'] = left_over
        #
        context['topic_points'] = topic_points
        context['deleted_topic_points'] = deleted_topic_points
        context['removed_topic_points'] = removed_topic_points
        return context


class EarningStatisticsView(
            LoginRequiredMixin,
            BaseBreadcrumbMixin,
            generic.ListView
        ):
    login_url = 'user:login'
    redirect_field_name = False
    template_name = "dashboard/earning/statistics.html"
    context_object_name = 'context'

    @cached_property
    def crumbs(self):
        return [
                ("dashboard", reverse("dashboard:index")),
                ("statistics", reverse("dashboard:earning_statistics"))
                ]

    def get_queryset(self):
        context = {}
        context['sidebar_active'] = 'earning/statistics'
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
