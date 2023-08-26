import statistics
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
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from braces.views import (
        LoginRequiredMixin,
        GroupRequiredMixin,
        SuperuserRequiredMixin,
    )
from user.models import User
from AI.models import (
        ContentGenerationJob,
        ContentPromptQuestion,
        ContentPromptTopic,
        ContentPromptPoint,
        Usage,
        Lesson,
        Lesson_part,
        Lesson_quiz
    )
from content.models import (
        Question,
        Point,
        Specification,
        Course,
        CourseVersion,
        CourseSubscription,
        CourseReview,
        QuestionTrack,
        UserPaper
    )
from content.util.GeneralUtil import (
        filter_drag_drop_selection,
        order_full_spec_content,
        order_live_spec_content,
        extract_active_spec_content,
        ChapterQuestionGenerator,
        detect_empty_content,
        monthly_sum_data_list,
        usage_monthly_sum_data_list,
        user_course_monthly_sum_data_list,
        user_course_usage_monthly_sum_data_list,
        performance_index_monthly_sum_data_list,
        author_user_clicks_data_list,
    )
from djstripe.models import (
        Customer,
        PaymentMethod,
        Price,
        Plan,
        Subscription,
        Charge,
        Session
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
        n_months = 6
        labels = []
        for i in range(n_months):
            month = current_month - relativedelta(months=i)
            formatted_month = month.strftime('%b %y')
            labels.append(formatted_month)
        labels.reverse()

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
                [ContentGenerationJob, Usage, Lesson_part], labels, 'created_at', n_months
            )
        total_tokens = ContentGenerationJob.objects.aggregate(Sum('total'))['total__sum']
        total_tokens += Usage.objects.aggregate(Sum('total'))['total__sum']
        total_tokens += Lesson_part.objects.aggregate(Sum('total'))['total__sum']
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
                ("content management", reverse("dashboard:student_contentmanagement")),
                ("perfromance", '')
                ]

    def get_queryset(self):
        context = {}
        course_id = self.kwargs['course_id']
        course = Course.objects.get(id=course_id)
        version = CourseVersion.objects.filter(course=course).order_by('-version_number')[0]
        #
        question_tracks = QuestionTrack.objects.filter(user=self.request.user, course=course)
        total_q_tracks = len(question_tracks.filter(track_attempt_number__gt=0))
        #

        #
        all_chapters = 0
        _, all_questions = extract_active_spec_content(version.version_content)
        total_n_questions = len(all_questions)
        all_chapters = total_n_questions//25
        #
        difficulty_statistics = []
        attempted_questions = question_tracks.filter(track_attempt_number__gt=0)
        all_question_marks = attempted_questions.aggregate(total_sum=Sum('total_marks'))['total_sum']
        all_attempt_marks = attempted_questions.aggregate(total_sum=Sum('track_mark'))['total_sum']
        all_questions_percentage = round(100*(all_attempt_marks/all_question_marks)) if all_attempt_marks and all_question_marks else 0
        #
        for difficulty in range(1, 6, 1):
            target_questions = attempted_questions.filter(question__q_difficulty=difficulty)
            #
            total_difficulty_answers = len(target_questions)
            total_question_marks = target_questions.aggregate(total_sum=Sum('total_marks'))['total_sum']
            total_attempt_marks = target_questions.aggregate(total_sum=Sum('track_mark'))['total_sum']
            #
            difficulty_statistics.append(
                (
                    difficulty,
                    total_difficulty_answers,
                    all_chapters*5,
                    round(100*(total_attempt_marks/total_question_marks)) if total_attempt_marks and total_question_marks else 0
                )
            )
        #
        lessons = Lesson.objects.filter(user=self.request.user, course=course)
        lesson_parts = Lesson_part.objects.filter(user=self.request.user, lesson__in=lessons)
        total_tokens = lesson_parts.aggregate(total_sum=Sum('total'))['total_sum']
        #
        quizzes = Lesson_quiz.objects.filter(user=self.request.user, course=course)
        completed_quizzes = quizzes.filter(completed=True)
        papers = UserPaper.objects.filter(user=self.request.user, pap_course=course)
        completed_papers = papers.filter(pap_completion=True)
        #
        total_tests = len(papers) + len(quizzes)
        total_completed_tests = len(completed_quizzes) + len(completed_papers)
        #
        quizzes_average_score = completed_quizzes.aggregate(total_sum=Sum('percentage_score'))['total_sum']/len(completed_quizzes) if completed_quizzes else 0
        papers_average_score = completed_papers.aggregate(total_sum=Sum('percentage_score'))['total_sum']/len(completed_papers) if completed_quizzes else 0
        total_average_score = (quizzes_average_score+papers_average_score)/2
        #
        context['course'] = course
        context['total_n_questions'] = total_n_questions
        context['total_q_tracks'] = total_q_tracks
        context['difficulty_statistics'] = difficulty_statistics
        context['total_tokens'] = total_tokens if total_tokens else 0
        context['total_tests'] = total_tests
        context['total_completed_tests'] = total_completed_tests
        context['total_average_score'] = round(total_average_score)
        context['all_questions_percentage'] = all_questions_percentage

        
        datasets = []
        current_month = datetime.now().date()
        n_months = 6
        labels = []
        for i in range(n_months):
            month = current_month - relativedelta(months=i)
            formatted_month = month.strftime('%b %y')
            labels.append(formatted_month)
        labels.reverse()
        usage_dataset = user_course_usage_monthly_sum_data_list(
                [Lesson_part], labels, lessons,'created_at', n_months
            )
        performance_index_data = performance_index_monthly_sum_data_list(
                QuestionTrack, labels, self.request.user, course, 'track_creation_time', n_months
            )
        datasets.append({
            "label": "Questions Answered",
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
            "data": performance_index_data
        })
        context['labels'] = labels
        context['datasets'] = datasets
        context['usage_dataset'] = usage_dataset
        #
        context['q_diff_pie_labels'] = [f"Difficulty {i}" for i in range(1, 6, 1)]
        context['q_diff_polar_labels'] = [f"Difficulty {i}" for i in range(1, 6, 1)]
        context['q_diff_dataset'] = [diff[1] for diff in difficulty_statistics]
        context['q_diff_polar_dataset'] = [diff[3] for diff in difficulty_statistics]
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
        context['CDN_URL'] = settings.CDN_URL
        return context


# Admin views
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
                ("mycourses", reverse("dashboard:mycourses")),
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
        content = spec.spec_content.copy()
        for module in content.keys():
            module_content = ChapterQuestionGenerator(
                    self.request.user,
                    spec.spec_subject,
                    module,
                    content[module]['content'].copy()
                )
            content[module]['content'] = module_content
        spec.spec_content = content
        spec.save()
        #
        empty_content = detect_empty_content(spec.spec_content)
        # get moduels from db
        author_confirmed_questions = Question.objects.values(
                    'q_subject',
                    'q_moduel',
                    'q_chapter',
                ).distinct().order_by(
                    'q_subject',
                    'q_moduel',
                    'q_chapter',
                ).filter(
                        user=self.request.user,
                        q_subject=subject,
                        erased=False,
                        deleted=False,
                        author_confirmation=False,
                )
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
        author_confirmed_chapters = all_chapters.filter(deleted=False, erased=False, author_confirmation=False)
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
        author_confirmed_module_chapters = collections.defaultdict(list)
        for confirmed_chapter in author_confirmed_chapters:
            author_confirmed_module_chapters[confirmed_chapter['p_moduel']].append(confirmed_chapter['p_chapter'])
        author_confirmed_chapter_questions = collections.defaultdict(list)
        for confirmed_q_chapters in author_confirmed_questions:
            author_confirmed_chapter_questions[confirmed_q_chapters['q_moduel']].append(confirmed_q_chapters['q_chapter'])
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
        context['empty_content'] = empty_content
        context['module_chapters'] = module_chapters
        context['author_confirmed_module_chapters'] = author_confirmed_module_chapters
        context['author_confirmed_chapter_questions'] = author_confirmed_chapter_questions
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
                ("mycourses", reverse("dashboard:mycourses")),
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
        empty_content = detect_empty_content(spec.spec_content)
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
        author_confirmed_questions = Question.objects.values(
                    'q_subject',
                    'q_moduel',
                    'q_chapter',
                    'q_difficulty',
                    'q_number',
                ).distinct().order_by(
                    'q_subject',
                    'q_moduel',
                    'q_chapter',
                ).filter(
                        user=self.request.user,
                        q_subject=subject,
                        q_moduel=moduel,
                        erased=False,
                        deleted=False,
                        author_confirmation=False,
                )
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
        author_confirmed_points = points.filter(author_confirmation=False)
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
        author_confirmed_topic_points = collections.defaultdict(list)
        for confirmed_points in author_confirmed_points:
            author_confirmed_topic_points[confirmed_points['p_topic']].append(confirmed_points['p_unique_id'])
        author_confirmed_chapter_questions = collections.defaultdict(list)
        for confirmed_q_chapters in author_confirmed_questions:
            author_confirmed_chapter_questions[str(confirmed_q_chapters['q_difficulty'])].append(confirmed_q_chapters['q_number'])
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
        context['empty_content'] = empty_content
        context['deleted_topics'] = deleted_objs
        context['removed_items'] = left_over
        #
        context['topic_points'] = topic_points
        context['author_confirmed_topic_points'] = author_confirmed_topic_points
        context['author_confirmed_chapter_questions'] = author_confirmed_chapter_questions if len(author_confirmed_chapter_questions) > 0 else None
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
        author_courses = Course.objects.filter(user=self.request.user)
        # Relevant locally
        all_course_subscriptions = CourseSubscription.objects.filter(course__in=author_courses)
        all_unique_students = all_course_subscriptions.values('user').distinct()
        # Relevant for stripe
        all_customers = Customer.objects.filter(
            id__in=list(all_unique_students.values_list('user__id', flat=True))
        )
        # Get the current date
        current_date = datetime.now().replace(day=1)

        # Initialize a list to store the last 6 months
        last_six_months = []
        presentable_last_six_months = []
        filterable_last_six_months = []

        # Calculate the last 6 months and add them to the list
        for i in range(6):
            current_date = current_date.replace(day=1)
            last_six_months.append(current_date.strftime('%Y%m'))
            presentable_last_six_months.append(current_date.strftime('%y %b'))
            filterable_last_six_months.append(current_date.strftime('%Y-%m-%d'))
            current_date -= timedelta(days=30)  # Approximate 30 days per month

        (
            aggrigate_monthly_clicks,
            courge_aggrigate_monthly_clicks,
            month_active_subscriptions,
            estimated_earnings,
            aggrigate_user_monthly_engagement
        ) = author_user_clicks_data_list(
                last_six_months[::-1],
                all_course_subscriptions,
                author_courses,
            )
        datasets = []
        aggrigate_monthly_clicks_value = list(aggrigate_monthly_clicks.values())
        datasets.append({
            "label": "Clicks (N)",
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
            "yAxisID": 'y',
            "data": aggrigate_monthly_clicks_value
        })
        aggrigate_user_monthly_engagement = [
                aggrigate_user_monthly_engagement[month].values()
                for month in aggrigate_user_monthly_engagement
            ]
        aggrigate_user_monthly_engagement = [100*statistics.mean(array) if len(array) > 0 else 0.0 for array in aggrigate_user_monthly_engagement]
        datasets.append({
            "label": "Average User Engagement (%)",
            "lineTension": 0.2,
            "backgroundColor": "",
            "borderColor": "#00ff22",
            "pointRadius": 3,
            "pointBackgroundColor": "#00ff22",
            "pointBorderColor": "#00ff22",
            "pointHoverRadius": 3,
            "pointHoverBackgroundColor": "rgba(78, 115, 223, 1)",
            "pointHoverBorderColor": "rgba(78, 115, 223, 1)",
            "pointHitRadius": 10,
            "pointBorderWidth": 2,
            "yAxisID": 'y1',
            "data": aggrigate_user_monthly_engagement
        })
        #
        context['labels'] = presentable_last_six_months[::-1]
        context['clicks_dataset'] = datasets
        #
        per_click_rate = 0.001
        context['per_click_rate'] = per_click_rate
        context['estimated_earnings'] = round(estimated_earnings, 3)
        context['total_course_clicks'] = courge_aggrigate_monthly_clicks
        context['total_month_active_course_subscriptions'] = month_active_subscriptions
        context['total_course_subscriptions'] = len(all_course_subscriptions)
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
