import collections
import pandas as pd
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
from content.models import (Point, Video, Specification, SpecificationSubscription)
from content.util.ContentCRUD import filter_drag_drop_selection


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


class SuperuserContentManagementView(
            LoginRequiredMixin,
            SuperuserRequiredMixin,
            BaseBreadcrumbMixin,
            generic.ListView
        ):
    login_url = 'user:login'
    redirect_field_name = False
    template_name = "dashboard/superuser/contentmanagement.html"
    context_object_name = 'context'

    @cached_property
    def crumbs(self):
        return [
                ("dashboard", reverse("dashboard:index")),
                ("traffic", reverse("dashboard:admin_traffic"))
                ]

    def get_queryset(self):
        context = {}
        context['sidebar_active'] = 'superuser/contentmanagement'
        context['bad_videos'] = Video.objects.filter(v_health=False)
        return context


class SuperuserSpecificationsView(
            LoginRequiredMixin,
            SuperuserRequiredMixin,
            BaseBreadcrumbMixin,
            generic.ListView
        ):
    login_url = 'user:login'
    redirect_field_name = False
    template_name = "dashboard/superuser/specifications.html"
    context_object_name = 'context'

    @cached_property
    def crumbs(self):
        return [
                ("dashboard", reverse("dashboard:index")),
                ("specifications", reverse("dashboard:superuser_specifications"))
                ]

    def get_queryset(self):
        context = {}
        context['sidebar_active'] = 'superuser/specifications'
        #
        Notes = Specification.objects.values(
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
        dic = {}
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
            dic[le][s][m].append(Specification.objects.get(pk=idd))
        context['specifications'] = dic
        return context


class SuperuserSpecModuelHandlerView(
            LoginRequiredMixin,
            SuperuserRequiredMixin,
            BaseBreadcrumbMixin,
            generic.ListView
        ):
    login_url = 'user:login'
    redirect_field_name = False
    template_name = "dashboard/superuser/specmoduelhandler.html"
    context_object_name = 'context'

    @cached_property
    def crumbs(self):
        return [
                ("dashboard", reverse("dashboard:index")),
                ("specifications", reverse("dashboard:superuser_specifications")),
                ("designer", '')
                ]

    def get_queryset(self):
        context = {}
        context['sidebar_active'] = 'superuser/specifications'
        # get kwargs
        level = self.kwargs['level']
        subject = self.kwargs['subject']
        board = self.kwargs['board']
        name = self.kwargs['name']
        # get spec from db
        spec = Specification.objects.get(
                spec_level=level,
                spec_subject=subject,
                spec_board=board,
                spec_name=name
                )
        # get moduels from db
        moduels = Point.objects.values(
                    'p_level',
                    'p_subject',
                    'p_moduel',
                ).distinct().order_by(
                    'p_level',
                    'p_subject',
                    'p_moduel',
                ).filter(
                        p_level=level,
                        p_subject=subject,
                )
        # reformat moduels
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
        # return result
        context['spec'] = spec
        context['sample_obj'] = moduels_objs[0]
        context['moduels'] = moduels_objs_final
        context['specification_moduels'] = final_spec_objs
        context['spec_active'] = spec.spec_health
        return context


class SuperuserSpecChapterHandlerView(
            LoginRequiredMixin,
            SuperuserRequiredMixin,
            BaseBreadcrumbMixin,
            generic.ListView
        ):
    login_url = 'user:login'
    redirect_field_name = False
    template_name = "dashboard/superuser/specchapterhandler.html"
    context_object_name = 'context'

    @cached_property
    def crumbs(self):
        return [
                ("dashboard", reverse("dashboard:index")),
                ("specifications", reverse("dashboard:superuser_specifications")),
                ("designer", '')
                ]

    def get_queryset(self):
        context = {}
        context['sidebar_active'] = 'superuser/specifications'
        #
        level = self.kwargs['level']
        subject = self.kwargs['subject']
        board = self.kwargs['board']
        name = self.kwargs['name']
        moduel = self.kwargs['module']
        spec = Specification.objects.get(
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
                        p_level=level,
                        p_subject=subject,
                        p_moduel=moduel,
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
        context['sample_obj'] = chapter_objs[0]
        context['chapters'] = chapter_objs_final
        context['specification_chapters'] = final_spec_objs
        # return result
        return context


class SuperuserSpecTopicHandlerView(
            LoginRequiredMixin,
            SuperuserRequiredMixin,
            BaseBreadcrumbMixin,
            generic.ListView
        ):
    login_url = 'user:login'
    redirect_field_name = False
    template_name = "dashboard/superuser/spectopichandler.html"
    context_object_name = 'context'

    @cached_property
    def crumbs(self):
        return [
                ("dashboard", reverse("dashboard:index")),
                ("specifications", reverse("dashboard:superuser_specifications")),
                ("designer", '')
                ]

    def get_queryset(self):
        context = {}
        context['sidebar_active'] = 'superuser/specifications'
        #
        level = self.kwargs['level']
        subject = self.kwargs['subject']
        board = self.kwargs['board']
        name = self.kwargs['name']
        moduel = self.kwargs['module']
        chapter = self.kwargs['chapter']
        spec = Specification.objects.get(
                spec_level=level,
                spec_subject=subject,
                spec_board=board,
                spec_name=name,
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
                        p_level=level,
                        p_subject=subject,
                        p_moduel=moduel,
                        p_chapter=chapter,
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
        context['sample_obj'] = topics_objs[0]
        context['topics'] = topic_objs_final
        context['specification_topics'] = final_spec_objs
        # return result
        return context


class SuperuserSpecPointHandlerView(
            LoginRequiredMixin,
            SuperuserRequiredMixin,
            BaseBreadcrumbMixin,
            generic.ListView
        ):
    login_url = 'user:login'
    redirect_field_name = False
    template_name = "dashboard/superuser/specpointhandler.html"
    context_object_name = 'context'

    @cached_property
    def crumbs(self):
        return [
                ("dashboard", reverse("dashboard:index")),
                ("specifications", reverse("dashboard:superuser_specifications")),
                ("designer", '')
                ]

    def get_queryset(self):
        context = {}
        context['sidebar_active'] = 'superuser/specifications'
        #
        level = self.kwargs['level']
        subject = self.kwargs['subject']
        board = self.kwargs['board']
        name = self.kwargs['name']
        moduel = self.kwargs['module']
        chapter = self.kwargs['chapter']
        topic = self.kwargs['topic']
        spec = Specification.objects.get(
                spec_level=level,
                spec_subject=subject,
                spec_board=board,
                spec_name=name,
                )
        points = Point.objects.values(
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
                        p_level=level,
                        p_subject=subject,
                        p_moduel=moduel,
                        p_chapter=chapter,
                        p_topic=topic,
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
        context['sample_obj'] = point_objs[0]
        context['points'] = point_objs_final
        context['specification_points'] = final_spec_objs
        # return result
        return context



# Create your views here.
class IndexView(
            LoginRequiredMixin,
            BaseBreadcrumbMixin,
            generic.ListView
        ):
    login_url = 'user:login'
    redirect_field_name = ''


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
            LoginRequiredMixin,
            GroupRequiredMixin,
            BaseBreadcrumbMixin,
            generic.ListView
        ):
    login_url = 'user:login'
    redirect_field_name = False
    group_required = u"Admin"
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
        user_subscriptions = SpecificationSubscription.objects.values('specification').filter(user=self.request.user)
        context['subscriptions'] = [obj['specification'] for obj in user_subscriptions]
        #
        Notes = Specification.objects.values(
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
                ).filter(spec_health=True)
        Notes_objs = [obj for obj in Notes]
        df = pd.DataFrame(Notes_objs)
        dic = {}
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
            dic[le][s][m].append(Specification.objects.get(pk=idd))
        context['specifications'] = dic
        return context


class TeacherClassesView(
            LoginRequiredMixin,
            GroupRequiredMixin,
            BaseBreadcrumbMixin,
            generic.ListView
        ):
    login_url = 'user:login'
    redirect_field_name = False
    group_required = u'Teacher'
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
            LoginRequiredMixin,
            GroupRequiredMixin,
            BaseBreadcrumbMixin,
            generic.ListView
        ):
    login_url = 'user:login'
    redirect_field_name = False
    group_required = u"PrivateTutor"
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
            LoginRequiredMixin,
            GroupRequiredMixin,
            BaseBreadcrumbMixin,
            generic.ListView
        ):
    login_url = 'user:login'
    redirect_field_name = False
    group_required = u"School"
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
            LoginRequiredMixin,
            GroupRequiredMixin,
            BaseBreadcrumbMixin,
            generic.ListView
        ):
    login_url = 'user:login'
    redirect_field_name = False
    group_required = u"TuitionCenter"
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
