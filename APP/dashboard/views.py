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
from view_breadcrumbs import BaseBreadcrumbMixin
from braces.views import (
        LoginRequiredMixin,
        GroupRequiredMixin,
        SuperuserRequiredMixin,
    )
from content.models import (
        Point,
        Specification,
        Collaborator,
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
                ("traffic", reverse("dashboard:admin_traffic"))
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
                ("MarketPlace", reverse("dashboard:marketplace"))
                ]

    def get_queryset(self):
        context = {}
        context['sidebar_active'] = 'dashboard/marketplace'
        courses = Course.objects.all(
                #course_publication=True,
                #deleted=False
                )
        context['courses'] = courses
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
                ("MarketPlace", reverse("dashboard:marketplace")),
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
            LoginRequiredMixin,
            BaseBreadcrumbMixin,
            generic.ListView
        ):
    login_url = 'user:login'
    redirect_field_name = ''

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
        versions = collections.defaultdict(list)
        for course in courses:
            courseversions = CourseVersion.objects.filter(course=course).order_by(
                        '-version_number'
                    )
            for version in courseversions:
                versions[course.id].append(version)

        context['sidebar_active'] = 'dashboard/mycourses'
        context['specs'] = specs
        context['courses'] = courses
        context['course_versions'] = versions
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
        context['sidebar_active'] = 'dashboard/specifications'
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
        #
        # got collaboration specs and transform them
        collaborations = Collaborator.objects.filter(
                orchistrator=self.request.user, deleted=False
            )
        distinct_collaborators = collaborations.distinct('user')
        final_collabs_dict = {}
        for collaborator in distinct_collaborators:
            all_collabs = collaborations.filter(user=collaborator.user)
            final_collabs_dict[collaborator.user.id] = [obj for obj in all_collabs]
        #
        #
        # get contribution specs and transform them
        contributions = Collaborator.objects.filter(
                user=self.request.user, deleted=False
            )
        distinct_assists = contributions.distinct('orchistrator')
        final_contributions_dict = {}
        for assist in distinct_assists:
            all_assists = contributions.filter(orchistrator=assist.orchistrator)
            final_contributions_dict[assist.orchistrator.id] = [obj for obj in all_assists]
        #
        #
        #
        context['MyCollaborations'] = final_collabs_dict
        context['MyContributions'] = final_contributions_dict
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
                spec_name=name
            )
        # Get neighbor specs
        neighbor_specs = Specification.objects.filter(
                user=self.request.user,
                spec_level=level,
                spec_subject=subject,
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
                        deleted=False,
                )
        moduels = chapters.values(
                    'p_level',
                    'p_subject',
                    'p_moduel',
                ).distinct().order_by(
                    'p_level',
                    'p_subject',
                    'p_moduel',
                )        # reformat moduels
        chapters_objs = [obj for obj in chapters]
        moduels_objs = [obj for obj in moduels]
        spec_content = spec.spec_content
        # get moduels already ordered saved previously
        dict2 = [
                str(content['position'])+'_'+key
                for key, content in spec_content.items()
            ]
        moduels_objs_final, final_spec_objs = filter_drag_drop_selection(
                moduels_objs, dict2, 'p_moduel'
            )
        # Remove hidden moduels from selection
        dict3 = [
                [
                    (str(chapter['position'])+'_'+key1, ordered_moduel)
                    for key1, chapter in spec_content[ordered_moduel['p_moduel']]['content'].items()
                ]
                    for ordered_moduel in final_spec_objs
            ]
        total_final_chapterspec_objs = []
        for dicc in dict3:
            if len(dicc) > 0:
                div_chapters = [c for c in chapters.filter(p_moduel=dicc[0][1]['p_moduel'])]
                chapters_objs_final, final_chapterspec_objs = filter_drag_drop_selection(
                         div_chapters,[a[0] for a in dicc], 'p_chapter'
                    )
                total_final_chapterspec_objs.extend(final_chapterspec_objs)
        # return result
        context['spec'] = spec
        context['sample_obj'] = moduels_objs[0] if len(moduels_objs) > 0 else None
        context['all_moduels'] = moduels_objs
        context['all_chapters'] = total_final_chapterspec_objs
        context['moduels'] = moduels_objs_final
        context['specification_moduels'] = final_spec_objs
        context['spec_completion'] = spec.spec_completion
        context['neighbor_specs'] = neighbor_specs
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
        user_subscriptions = CourseSubscription.objects.filter(user=self.request.user)
        context['subscriptions'] = [obj.course for obj in user_subscriptions]
        return context


class EditorTasksView(
            LoginRequiredMixin,
            GroupRequiredMixin,
            BaseBreadcrumbMixin,
            generic.ListView
        ):
    login_url = 'user:login'
    redirect_field_name = False
    group_required = u"Editor"
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


class EditorMyTasksView(
            LoginRequiredMixin,
            GroupRequiredMixin,
            BaseBreadcrumbMixin,
            generic.ListView
        ):
    login_url = 'user:login'
    redirect_field_name = False
    group_required = u"Editor"
    template_name = "dashboard/editor/mytasks.html"
    context_object_name = 'context'

    @cached_property
    def crumbs(self):
        return [
                ("dashboard", reverse("dashboard:index")),
                ("mytasks", reverse("dashboard:editor_mytasks"))
                ]

    def get_queryset(self):
        context = {}
        context['sidebar_active'] = 'editor/mytasks'
        return context


class EditorEditorView(
            LoginRequiredMixin,
            GroupRequiredMixin,
            BaseBreadcrumbMixin,
            generic.ListView
        ):
    login_url = 'user:login'
    redirect_field_name = False
    group_required = u"Editor"
    template_name = "dashboard/editor/editor.html"
    context_object_name = 'context'

    @cached_property
    def crumbs(self):
        return [
                ("dashboard", reverse("dashboard:index")),
                ("editor", reverse("dashboard:editor_editor"))
                ]

    def get_queryset(self):
        context = {}
        context['sidebar_active'] = 'editor/editor'
        return context


class AffiliateStatisticsView(
            LoginRequiredMixin,
            GroupRequiredMixin,
            BaseBreadcrumbMixin,
            generic.ListView
        ):
    login_url = 'user:login'
    redirect_field_name = False
    group_required = u'Affiliate'
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
