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


class SpecificationOutlineView(
            LoginRequiredMixin,
            BaseBreadcrumbMixin,
            generic.ListView
        ):
    login_url = 'user:login'
    redirect_field_name = False
    template_name = "dashboard/general/specificationoutline.html"
    context_object_name = 'context'

    @cached_property
    def crumbs(self):
        return [
                ("dashboard", reverse("dashboard:index")),
                ("specifications", reverse("dashboard:specifications")),
                ("outline", '')
                ]

    def get_queryset(self):
        context = {}
        context['sidebar_active'] = 'dashboard/general/specificationoutline.html'
        spec_id = self.kwargs['spec_id']
        #
        spec = Specification.objects.get(
                    user=self.request.user,
                    pk=spec_id
                )
        content = order_live_spec_content(spec.spec_content)
        context['spec'] = spec
        context['ordered_content'] = content
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
        chapters = Point.objects.values(
                    'p_level',
                    'p_subject',
                    'p_moduel',
                    'p_chapter',
                    'is_completed_content',
                    'is_completed_questions',
                ).distinct().order_by(
                    'p_level',
                    'p_subject',
                    'p_moduel',
                    'p_chapter',
                ).filter(
                        user=self.request.user,
                        p_level=level,
                        p_subject=subject,
                )
        deleted_chapters = chapters.filter(deleted=True, erased=False)
        chapters = chapters.filter(deleted=False, erased=False)
        moduels = chapters.values(
                    'p_level',
                    'p_subject',
                    'p_moduel',
                ).distinct().order_by(
                    'p_level',
                    'p_subject',
                    'p_moduel',
                )        # reformat moduels
        deleted_moduels = deleted_chapters.values(
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
        deleted_objs = [obj['p_moduel'] for obj in deleted_moduels]
        ordered_spec = order_full_spec_content(spec.spec_content)
        keys = list(ordered_spec.keys())
        left_over = [mod for mod in moduels_objs if mod not in keys]
        moduels_objs = left_over + keys
        #
        context['spec'] = spec
        context['modules'] = moduels_objs
        context['deleted_moduels'] = deleted_objs
        context['full_ord_spec'] = ordered_spec
        return context


class SpecChapterHandlerView(
            LoginRequiredMixin,
            BaseBreadcrumbMixin,
            generic.ListView
        ):
    login_url = 'user:login'
    redirect_field_name = False
    template_name = "dashboard/general/specchapterhandler.html"
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
        spec = Specification.objects.get(
                user=self.request.user,
                spec_level=level,
                spec_subject=subject,
                spec_board=board,
                spec_name=name,
                )
        chapters = Point.objects.values(
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
                        p_moduel=moduel,
                        deleted=False,
                )
        chapter_objs = [obj for obj in chapters]
        moduel_content = spec.spec_content[moduel]['content']
        dict2 = [
                str(content['position'])+'_'+key
                for key, content in moduel_content.items()
            ]
        chapter_objs_final, final_spec_objs = filter_drag_drop_selection(
                chapter_objs, dict2, 'p_chapter'
            )
        context['spec'] = spec
        context['sample_obj'] = chapter_objs[0] if len(chapter_objs) > 0 else None
        context['all_chapters'] = chapter_objs
        context['chapters'] = chapter_objs_final
        context['specification_chapters'] = final_spec_objs
        # return result
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
                deleted=False
                )
        topics = Point.objects.values(
                    'p_level',
                    'p_subject',
                    'p_moduel',
                    'p_chapter',
                    'p_topic',
                ).distinct().order_by(
                    'p_level',
                    'p_subject',
                    'p_moduel',
                    'p_chapter',
                    'p_topic',
                ).filter(
                        user=self.request.user,
                        p_level=level,
                        p_subject=subject,
                        p_moduel=moduel,
                        p_chapter=chapter,
                        deleted=False
                )
        topics_objs = [obj for obj in topics]
        chapter_content = spec.spec_content[moduel]['content'][chapter]['content']
        dict2 = [
                str(content['position'])+'_'+key
                for key, content in chapter_content.items()
            ]
        topic_objs_final, final_spec_objs = filter_drag_drop_selection(
                topics_objs, dict2, 'p_topic'
            )
        context['spec'] = spec
        context['sample_obj'] = topics_objs[0] if len(topics_objs) > 0 else None
        context['all_topics'] = topics_objs
        context['topics'] = topic_objs_final
        context['specification_topics'] = final_spec_objs
        # return result
        return context


class SpecPointHandlerView(
            LoginRequiredMixin,
            BaseBreadcrumbMixin,
            generic.ListView
        ):
    login_url = 'user:login'
    redirect_field_name = False
    template_name = "dashboard/general/specpointhandler.html"
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
        topic = self.kwargs['topic']
        spec = Specification.objects.get(
                user=self.request.user,
                spec_level=level,
                spec_subject=subject,
                spec_board=board,
                spec_name=name,
                deleted=False
                )
        points = Point.objects.values(
                    'id',
                    'p_level',
                    'p_subject',
                    'p_moduel',
                    'p_chapter',
                    'p_topic',
                    'p_number',
                    'p_content',
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
                        p_topic=topic,
                        deleted=False
                )
        point_objs = [obj for obj in points]
        chapter_content = spec.spec_content[moduel]['content'][chapter]['content'][topic]['content']
        dict2 = [
                str(content['position'])+'_'+key
                for key, content in chapter_content.items()
            ]
        point_objs_final, final_spec_objs = filter_drag_drop_selection(
                point_objs, dict2, 'p_unique_id'
            )
        context['spec'] = spec
        context['sample_obj'] = point_objs[0] if len(point_objs) > 0 else None
        context['points'] = point_objs_final
        context['all_points'] = point_objs
        context['specification_points'] = final_spec_objs
        # return result
        return context


# Create your views here.
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


class CollabContributeView(
            LoginRequiredMixin,
            GroupRequiredMixin,
            BaseBreadcrumbMixin,
            generic.ListView
        ):
    login_url = 'user:login'
    redirect_field_name = False
    group_required = u"Student"
    template_name = "dashboard/collaborator/contribute.html"
    context_object_name = 'context'

    @cached_property
    def crumbs(self):
        return [
                ("dashboard", reverse("dashboard:index")),
                ("contribute", reverse("dashboard:collab_contribute"))
                ]

    def get_queryset(self):
        context = {}
        context['sidebar_active'] = 'collaborator/contribute'
        # get contribution specs and transform them
        contributions = Collaborator.objects.filter(
                user=self.request.user, deleted=False
            )
        distinct_assists = contributions.distinct('orchistrator')
        raw_specs = Specification.objects.filter(
                user=self.request.user, deleted=False
            )
        final_contributions_dict = {}
        for assist in distinct_assists:
            all_assists = contributions.filter(orchistrator=assist.orchistrator)
            collab_spec = [collab.specification.id for collab in all_assists]
            valid_specs = raw_specs.exclude(id__in=collab_spec)
            #
            freelance = all_assists.filter(collaborator_type=1).order_by('specification')
            partner = all_assists.filter(collaborator_type=2).order_by('specification')
            volenteer = all_assists.filter(collaborator_type=3).order_by('specification')
            #
            final_contributions_dict[assist.orchistrator.id] = (
                    assist.orchistrator, freelance, partner, volenteer, valid_specs
                )
        #
        context['domain'] = settings.SITE_URL
        context['MyContributions'] = final_contributions_dict
        context['raw_specs'] = raw_specs
        return context


class CollabContributeManagerView(
            LoginRequiredMixin,
            GroupRequiredMixin,
            BaseBreadcrumbMixin,
            generic.ListView
        ):
    login_url = 'user:login'
    redirect_field_name = False
    group_required = u"Student"
    template_name = "dashboard/collaborator/contribute_manager.html"
    context_object_name = 'context'

    @cached_property
    def crumbs(self):
        return [
                ("dashboard", reverse("dashboard:index")),
                ("contribute", reverse("dashboard:collab_contribute")),
                ("manager", '')
                ]

    def get_queryset(self):
        context = {}
        context['sidebar_active'] = 'collaborator/contribute_manager'
        collaboration_id = self.kwargs['contribution_id']
        collaboration = Collaborator.objects.get(pk=collaboration_id)
        tasks = ContributionTask.objects.filter(
                collaboration=collaboration
            ).order_by('-created_at')
        spec = collaboration.specification
        content = order_live_spec_content(spec.spec_content)
        modules = list(content.keys())
        chapters = collections.OrderedDict({})
        unclaimables = set()
        for module in modules:
            _chapters = list(content[module]['content'].keys())
            chapters[module] = _chapters
        # Apply task exclusions
        all_spec_collaborations = Collaborator.objects.filter(
                specification=collaboration.specification,
                active=True,
                deleted=False,
            )
        claimed_modules = ContributionTask.objects.filter(
                collaboration__in=all_spec_collaborations,
                task_chapter='Null',
                ended=False
            )
        claimed_chapters = ContributionTask.objects.filter(
                collaboration__in=all_spec_collaborations,
                ended=False
            ).exclude(task_chapter='Null')
        for claimed_mod in claimed_modules:
            idx = modules.index(claimed_mod.task_moduel)
            del modules[idx]
        for claimed_chap in claimed_chapters:
            idx = chapters[claimed_chap.task_moduel].index(claimed_chap.task_chapter)
            del chapters[claimed_chap.task_moduel][idx]
        for task in tasks:
            if task.task_chapter != 'Null':
                unclaimables.add(task.task_moduel)
        context['unclaimable_modules'] = unclaimables
        context['collaboration'] = collaboration
        context['tasks'] = tasks
        context['modules'] = modules
        context['module_chapters'] = chapters
        return context


class CollabReviewView(
            LoginRequiredMixin,
            GroupRequiredMixin,
            BaseBreadcrumbMixin,
            generic.ListView
        ):
    login_url = 'user:login'
    redirect_field_name = False
    group_required = u"Student"
    template_name = "dashboard/collaborator/review_work.html"
    context_object_name = 'context'

    @cached_property
    def crumbs(self):
        return [
                ("dashboard", reverse("dashboard:index")),
                ("review", reverse("dashboard:collab_review"))
                ]

    def get_queryset(self):
        context = {}
        context['sidebar_active'] = 'collaborator/review'
        return context


class CollabManageView(
            LoginRequiredMixin,
            GroupRequiredMixin,
            BaseBreadcrumbMixin,
            generic.ListView
        ):
    login_url = 'user:login'
    redirect_field_name = False
    group_required = u"Student"
    template_name = "dashboard/collaborator/manage_collaborations.html"
    context_object_name = 'context'

    @cached_property
    def crumbs(self):
        return [
                ("dashboard", reverse("dashboard:index")),
                ("collaborations", reverse("dashboard:collab_manage"))
                ]

    def get_queryset(self):
        context = {}
        context['sidebar_active'] = 'collaborator/collaborations'
        # get contribution specs and transform them
        contributions = Collaborator.objects.filter(
                user=self.request.user, deleted=False
            )
        distinct_assists = contributions.distinct('orchistrator')
        raw_specs = Specification.objects.filter(
                user=self.request.user, deleted=False
            )
        final_contributions_dict = {}
        for assist in distinct_assists:
            all_assists = contributions.filter(orchistrator=assist.orchistrator)
            collab_spec = [collab.specification.id for collab in all_assists]
            valid_specs = raw_specs.exclude(id__in=collab_spec)
            #
            freelance = all_assists.filter(collaborator_type=1).order_by('specification')
            partner = all_assists.filter(collaborator_type=2).order_by('specification')
            volenteer = all_assists.filter(collaborator_type=3).order_by('specification')
            #
            final_contributions_dict[assist.orchistrator.id] = (
                    assist.orchistrator, freelance, partner, volenteer, valid_specs
                )
        #
        context['domain'] = settings.SITE_URL
        context['MyContributions'] = final_contributions_dict
        context['raw_specs'] = raw_specs
        return context


class CollaboratorsManageView(
            LoginRequiredMixin,
            GroupRequiredMixin,
            BaseBreadcrumbMixin,
            generic.ListView
        ):
    login_url = 'user:login'
    redirect_field_name = False
    group_required = u"Student"
    template_name = "dashboard/collaborator/manage_collaborators.html"
    context_object_name = 'context'

    @cached_property
    def crumbs(self):
        return [
                ("dashboard", reverse("dashboard:index")),
                ("review", reverse("dashboard:collaborators_manage"))
                ]

    def get_queryset(self):
        context = {}
        context['sidebar_active'] = 'collaborator/collaborators'
        # got collaboration specs and transform them
        collaborations = Collaborator.objects.filter(
                orchistrator=self.request.user, deleted=False
            )
        distinct_collaborators = collaborations.distinct('user')
        raw_specs = Specification.objects.filter(
                user=self.request.user, deleted=False
            )
        final_collabs_dict = {}
        for collaborator in distinct_collaborators:
            all_collabs = collaborations.filter(user=collaborator.user)
            collab_spec = [collab.specification.id for collab in all_collabs]
            valid_specs = raw_specs.exclude(id__in=collab_spec)
            #
            freelance = all_collabs.filter(collaborator_type=1).order_by('specification')
            partner = all_collabs.filter(collaborator_type=2).order_by('specification')
            volenteer = all_collabs.filter(collaborator_type=3).order_by('specification')
            #
            final_collabs_dict[collaborator.user.id] = (
                    collaborator.user, freelance, partner, volenteer, valid_specs
                )
        #
        #
        context['MyCollaborations'] = final_collabs_dict
        context['raw_specs'] = raw_specs
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
