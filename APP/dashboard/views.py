import collections
from django.conf import settings
from django.urls import reverse
from django.views import generic
from django.utils.functional import cached_property
from django.core.paginator import Paginator, EmptyPage
from view_breadcrumbs import BaseBreadcrumbMixin
from django.db.models import Count, Avg
from django.contrib.postgres.search import (
        SearchVector, SearchQuery, SearchRank
    )
from django.db.models import Sum
from datetime import datetime
from dateutil.relativedelta import relativedelta
from braces.views import (
        SuperuserRequiredMixin,
    )
from PP2.mixin import (
        LoginRequiredMixin,
        CourseSubscriptionRequiredMixin,
        AuthorRequiredMixin,
    )
from user.models import User
from AI.models import (
        Lesson_quiz
    )
from content.models import (
        Course,
        CourseVersion,
        CourseSubscription,
        CourseReview,
        QuestionTrack,
        UserPaper
    )
from content.util.GeneralUtil import (
        extract_active_spec_content,
        monthly_sum_data_list,
        performance_index_monthly_sum_data_list,
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
        return context


class StudentPerformanceView(
            LoginRequiredMixin,
            CourseSubscriptionRequiredMixin,
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
        quizzes = Lesson_quiz.objects.filter(user=self.request.user, course=course)
        completed_quizzes = quizzes.filter(completed=True)
        papers = UserPaper.objects.filter(user=self.request.user, pap_course=course)
        completed_papers = papers.filter(pap_completion=True)
        #
        total_tests = len(papers) + len(quizzes)
        total_completed_tests = len(completed_quizzes) + len(completed_papers)
        #
        quizzes_average_score = completed_quizzes.aggregate(total_sum=Sum('percentage_score'))['total_sum']/len(completed_quizzes) if completed_quizzes else 0
        papers_average_score = completed_papers.aggregate(total_sum=Sum('percentage_score'))['total_sum']/len(completed_papers) if completed_papers else 0
        #
        total_average_score = (quizzes_average_score+papers_average_score)/2
        #
        context['course'] = course
        context['total_n_questions'] = total_n_questions
        context['total_q_tracks'] = total_q_tracks
        context['difficulty_statistics'] = difficulty_statistics
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
        #
        context['q_diff_pie_labels'] = [f"Difficulty {i}" for i in range(1, 6, 1)]
        context['q_diff_polar_labels'] = [f"Difficulty {i}" for i in range(1, 6, 1)]
        context['q_diff_dataset'] = [diff[1] for diff in difficulty_statistics]
        context['q_diff_polar_dataset'] = [diff[3] for diff in difficulty_statistics]
        return context


class StudentContentManagementView(
            LoginRequiredMixin,
            BaseBreadcrumbMixin,
            generic.ListView
        ):
    login_url = 'user:login'
    redirect_field_name = False
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
            AuthorRequiredMixin,
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
class BlankView(BaseBreadcrumbMixin, generic.ListView):
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


class NotFoundView(BaseBreadcrumbMixin, generic.ListView):
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
