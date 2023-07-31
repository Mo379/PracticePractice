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
from django.db.models import CharField, Count, Avg
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank
from django.db.models.functions import TruncMonth
from django.db.models import Count, Sum
from datetime import datetime
from dateutil.relativedelta import relativedelta
from braces.views import (
        LoginRequiredMixin,
        GroupRequiredMixin,
        SuperuserRequiredMixin,
    )
from AI.models import (
        ContentGenerationJob,
        ContentPromptQuestion,
        ContentPromptTopic,
        ContentPromptPoint,
        Usage,
    )
from user.models import User
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
                ("Home", reverse("main:index")),
                ]

    def get_queryset(self):
        context = {}
        users = User.objects.count()
        subscriptions = CourseSubscription.objects.count()
        courses = Course.objects.count()
        context['sidebar_active'] = 'superuser/monitor'
        context['users'] = users
        context['subscriptions'] = subscriptions
        context['courses'] = courses
        #
        datasets = []

        current_month = datetime.now().date()
        n_months = 12
        labels = []
        for i in range(n_months):
            month = current_month - relativedelta(months=i)
            formatted_month = month.strftime('%b %y')
            labels.append(formatted_month)
        labels.reverse()

        def monthly_sum_data_list(
                    Model,
                    labels,
                    time_field='date_joined',
                    n_months=n_months,
                    count_fn=Count('id')
                ):
            data = [0 for _ in range(n_months)]
            data_aggr = Model.objects.annotate(
                    month=TruncMonth(time_field)
                ).values(
                    'month'
                ).annotate(
                    count=count_fn
                    ).values('month', 'count')[0:n_months]
            for count in data_aggr:
                month = count['month'].strftime('%b %y')
                user_count = count['count']
                if month in labels:
                    idd = labels.index(month)
                    data[idd] = user_count
            return data

        def usage_monthly_sum_data_list(
                    models, labels, time_field='created_at', n_months=n_months
                ):
            Prompt = [0 for _ in range(n_months)]
            Completion = [0 for _ in range(n_months)]
            Total = [0 for _ in range(n_months)]
            for model in models:
                for field in ['prompt', 'completion', 'total']:
                    data_set = monthly_sum_data_list(model, labels, time_field, n_months, Sum(field))
                    if field == 'prompt':
                        Prompt = [sum(x) for x in zip(Prompt, data_set)]
                    if field == 'completion':
                        Completion = [sum(x) for x in zip(Completion, data_set)]
                    if field == 'total':
                        Total = [sum(x) for x in zip(Total, data_set)]
            datasets = []
            for field in [
                    ('prompt', Prompt, '#f6c23e'),
                    ('completion', Completion, '#1cc88a'),
                    ('total', Total, '#36b9cc')
                ]:
                datasets.append({
                    "label": field[0].upper(),
                    "lineTension": 0.2,
                    "backgroundColor": "",
                    "borderColor": field[2],
                    "pointRadius": 3,
                    "pointBackgroundColor": field[2],
                    "pointBorderColor": field[2],
                    "pointHoverRadius": 3,
                    "pointHoverBackgroundColor": "rgba(78, 115, 223, 1)",
                    "pointHoverBorderColor": "rgba(78, 115, 223, 1)",
                    "pointHitRadius": 10,
                    "pointBorderWidth": 2,
                    "data":  field[1]
                })
            return datasets

        user_data = monthly_sum_data_list(
                User, labels, 'date_joined', n_months
            )
        course_data = monthly_sum_data_list(
                Course, labels, 'course_created_at', n_months
            )
        subscription_data = monthly_sum_data_list(
                CourseSubscription, labels, 'subscription_created_at', n_months
            )
        usage_dataset = usage_monthly_sum_data_list(
                [ContentGenerationJob, Usage], labels, 'created_at', n_months
            )
        total_tokens = ContentGenerationJob.objects.aggregate(Sum('total'))['total__sum']
        total_tokens += Usage.objects.aggregate(Sum('total'))['total__sum']
        context['total_tokens'] = total_tokens

        #
        datasets.append({
            "label": "Users",
            "lineTension": 0.2,
            "backgroundColor": "",
            "borderColor": "#f6c23e",
            "pointRadius": 3,
            "pointBackgroundColor": "#f6c23e",
            "pointBorderColor": "#f6c23e",
            "pointHoverRadius": 3,
            "pointHoverBackgroundColor": "rgba(78, 115, 223, 1)",
            "pointHoverBorderColor": "rgba(78, 115, 223, 1)",
            "pointHitRadius": 10,
            "pointBorderWidth": 2,
            "data": user_data
        })
        datasets.append({
            "label": "Courses",
            "lineTension": 0.2,
            "backgroundColor": "",
            "borderColor": "#1cc88a",
            "pointRadius": 3,
            "pointBackgroundColor": "#1cc88a",
            "pointBorderColor": "#1cc88a",
            "pointHoverRadius": 3,
            "pointHoverBackgroundColor": "rgba(78, 115, 223, 1)",
            "pointHoverBorderColor": "rgba(78, 115, 223, 1)",
            "pointHitRadius": 10,
            "pointBorderWidth": 2,
            "data": course_data
        })
        datasets.append({
            "label": "Course Subscriptions",
            "lineTension": 0.2,
            "backgroundColor": "",
            "borderColor": "#36b9cc",
            "pointRadius": 3,
            "pointBackgroundColor": "#36b9cc",
            "pointBorderColor": "#36b9cc",
            "pointHoverRadius": 3,
            "pointHoverBackgroundColor": "rgba(78, 115, 223, 1)",
            "pointHoverBorderColor": "rgba(78, 115, 223, 1)",
            "pointHitRadius": 10,
            "pointBorderWidth": 2,
            "data": subscription_data
        })
        context['labels'] = labels
        context['datasets'] = datasets
        context['usage_dataset'] = usage_dataset
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
                ("Home", reverse("main:index")),
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
                ("Home", reverse("main:index")),
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
                ("Home", reverse("main:index")),
                ("MyCourses", reverse("dashboard:mycourses"))
                ]

    def get_queryset(self):
        context = {}
        context['sidebar_active'] = 'writer/mycourses'
        current_page = self.kwargs['page'] if 'page' in self.kwargs else 1
        #
        specs = Specification.objects.filter(
                    user=self.request.user,
                    deleted=False
                )
        courses = Course.objects.filter(
                    user=self.request.user,
                    deleted=False
                ).order_by(
                        '-course_created_at'
                    )
        specs = specs.exclude(pk__in=[course.specification.pk for course in courses])
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
                        )[:3]
            final_courses.append((courseversions, course))
        p = Paginator(final_courses, 9)
        try:
            context['courses'] = p.page(current_page)
        except EmptyPage:
            context['courses'] = p.page(p.num_pages)
            current_page = p.num_pages
        total_learners = CourseSubscription.objects.filter(
                course__in=courses
                ).values('course_id').annotate(count=Count('course'))
        course_sub_counts = {}
        for subscription in total_learners:
            course_sub_counts[int(subscription['course_id'])] = subscription['count']
        for key in courses:
            if key.id not in course_sub_counts.keys():
                course_sub_counts[key.id] = 0
        #
        all_reviews = CourseReview.objects.filter(course__in=courses)
        avg_reviews = all_reviews.values('course_id').annotate(rating=Avg('rating'), count=Count('id'))
        reviews = collections.defaultdict(list)
        for review in avg_reviews:
            reviews[int(subscription['course_id'])] = [review['rating'], review['count']]
        for key in courses:
            if key.id not in reviews.keys():
                reviews[key.id] = [0.0, 0]
        #
        context['course_sub_counts'] = course_sub_counts
        context['reviews'] = reviews
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
                ("Home", reverse("main:index")),
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
                ("Home", reverse("main:index")),
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
                ("Home", reverse("main:index")),
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
        question_prompts = collections.defaultdict(list)
        for q_level in questions.keys():
            level_questions = questions[q_level]
            qs = Question.objects.filter(q_unique_id__in=level_questions).order_by('q_number')
            questions[q_level] = qs
            q_prompts, _ = ContentPromptQuestion.objects.get_or_create(
                    user=self.request.user,
                    specification=spec,
                    moduel=moduel,
                    chapter=chapter,
                    level=q_level
                )
            question_prompts[q_level].append(q_prompts)

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
        topic_prompts = collections.defaultdict(list)
        for key in keys:
            topic_points[key] = ordered_spec[key]['content'].keys()
            t_prompt, _ = ContentPromptTopic.objects.get_or_create(
                    user=self.request.user,
                    specification=spec,
                    moduel=moduel,
                    chapter=chapter,
                    topic=key
                )
            topic_prompts[key].append(t_prompt)
        #
        deleted_topic_points = collections.defaultdict(list)
        for d_points in deleted_points:
            deleted_topic_points[d_points['p_topic']].append(d_points['p_unique_id'])
        #
        removed_topic_points = collections.defaultdict(list)
        point_prompts = collections.defaultdict(dict)
        for topic in keys:
            for point in points.filter(p_topic=topic):
                if point['p_unique_id'] not in ordered_spec[topic]['content'].keys():
                    removed_topic_points[topic].append(point['p_unique_id'])
                p_prompt, _ = ContentPromptPoint.objects.get_or_create(
                        user=self.request.user,
                        specification=spec,
                        moduel=moduel,
                        chapter=chapter,
                        topic=topic,
                        p_unique=point['p_unique_id']
                    )
                point_prompts[topic][point['p_unique_id']] = p_prompt
        #
        generation_jobs = ContentGenerationJob.objects.filter(
                user=self.request.user,
                specification=spec,
                moduel=moduel,
                chapter=chapter,
            ).order_by('-created_at')
        if len(generation_jobs) > 0:
            last_job = generation_jobs[0]
        else:
            last_job = False
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
        #
        context['last_job'] = last_job
        context['q_prompts'] = question_prompts
        context['t_prompts'] = topic_prompts
        context['p_prompts'] = point_prompts
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
                ("Home", reverse("main:index")),
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
                ("Home", reverse("main:index")),
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
                ("Home", reverse("main:index")),
                ("404", reverse("dashboard:404"))
                ]

    def get_queryset(self):
        return "user_index"
