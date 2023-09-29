import pandas as pd
from django.conf import settings
import collections
from itertools import chain
from collections import OrderedDict
from django.shortcuts import redirect
from django.urls import reverse
from django.http import JsonResponse
from django.utils.functional import cached_property
from django.contrib import messages
from django.views import generic
from django.core.paginator import Paginator, EmptyPage
from django.contrib.postgres.search import (
        SearchVector, SearchQuery, SearchRank
    )
from django.db.models import Count, Avg
from content.util.GeneralUtil import (
        TagGenerator,
        order_full_spec_content,
        order_live_spec_content,
    )
from view_breadcrumbs import BaseBreadcrumbMixin
from django.forms import model_to_dict
from content.models import *
from content.util.GeneralUtil import (
        increment_course_subscription_significant_click,
        detect_empty_content,
        extract_active_spec_content,
        extract_active_spec_questions,
        confirm_question_checks,
        confirm_point_checks,
    )
from management.templatetags.general import ToMarkdownAnswerManual
from django.contrib.auth.decorators import login_required
from PP2.mixin import (
        LoginRequiredMixin,
        AnySubscriptionRequiredMixin,
        AnySubscriptionRequiredDec,
        AISubscriptionRequiredMixin,
        AISubscriptionRequiredDec,
        CourseSubscriptionRequiredMixin,
        CourseSubscriptionRequiredDec,
        AuthorRequiredMixin,
        AuthorRequiredDec,
        AffiliateRequiredMixin,
        AffiliateRequiredDec,
        TrusteeRequiredMixin,
        TrusteeRequiredDec
    )
from io import BytesIO
from PP2.utils import h_encode, h_decode
from AI.models import (
        Lesson_quiz,
    )
from djstripe.models import (
        Subscription,
    )
from AI import workflows


class ContentView(
        LoginRequiredMixin,
        BaseBreadcrumbMixin,
        generic.ListView
        ):
    login_url = 'user:login'
    redirect_field_name = False
    template_name = 'content/content.html'
    context_object_name = 'context'

    @cached_property
    def crumbs(self):
        return [
                ("content", reverse("content:content"))
                ]

    def get_queryset(self):
        """Return all of the required hub information"""
        context = {}
        current_page = self.kwargs['page'] if 'page' in self.kwargs else 1
        course_subscriptions = CourseSubscription.objects.filter(
                user=self.request.user,
                visibility=True,
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
        p = Paginator(courses, 9)
        try:
            context['courses'] = p.page(current_page)
        except EmptyPage:
            context['courses'] = p.page(p.num_pages)
            current_page = p.num_pages
        #
        total_learners = CourseSubscription.objects.filter(
                course__in=context['courses']
                ).values('course_id').annotate(count=Count('course'))
        course_sub_counts = {}
        for subscription in total_learners:
            course_sub_counts[int(subscription['course_id'])] = subscription['count']
        for key in context['courses']:
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


class NoteArticleView(
        BaseBreadcrumbMixin,
        generic.ListView
        ):
    template_name = 'content/note.html'
    context_object_name = 'context'

    @cached_property
    def crumbs(self):
        return [
                ("content", reverse("content:content")),
                ("coursestudy", reverse("content:coursestudy", kwargs={'course_id':self.kwargs['course_id']})),
                ("article", ''),
                ]

    def get_queryset(self):
        """Return all of the required hub information"""
        context = {}
        # Get details of page
        course_id = self.kwargs['course_id']
        module = self.kwargs['module']
        chapter = self.kwargs['chapter']
        context['title'] = chapter
        #
        course = Course.objects.get(
                    pk=course_id
                )
        if self.request.user.is_authenticated:
            course_subscription = CourseSubscription.objects.filter(
                    user=self.request.user,
                    course=course
                )
            if len(course_subscription) > 0:
                course_subscription = course_subscription[0]
                #
                if module not in course_subscription.progress_track.keys():
                    course_subscription.progress_track[module] = {}
                if chapter not in course_subscription.progress_track[module].keys():
                    course_subscription.progress_track[module][chapter] = {}
                if 'content' not in course_subscription.progress_track[module][chapter].keys():
                    course_subscription.progress_track[module][chapter]['content'] = True
                course_subscription.save()
        #
        source_spec = course.specification
        content = CourseVersion.objects.filter(
                course=course
            ).order_by('-version_number')[0].version_content
        #
        content = order_full_spec_content(content)
        #
        chapter_info = content[module]['content'][chapter]
        keys = [
                k for k, v in
                content[module]['content'].items() if v['position'] >= 0
            ]
        previous_chapter = chapter_info['position'] - 1 \
                if chapter_info['position'] > 0 else None
        next_chapter = chapter_info['position'] + 1 \
                if len(keys) > chapter_info['position'] + 1 else None
        #
        previous_link = keys[previous_chapter] if type(previous_chapter) == int else None
        next_link = keys[next_chapter] if type(next_chapter) == int else None
        #
        chapter_content = chapter_info['content']
        filtered_chapter_content = OrderedDict({
                key: val
                for key, val in chapter_content.items()
                if val['active'] == True
            })
        article_objects = []
        for topic, topic_info in filtered_chapter_content.items():
            for point_unique, info in topic_info['content'].items():
                if info['active'] == True:
                    obj = Point.objects.get(p_unique_id=point_unique)
                    article_objects.append(obj)
        #
        article_points = [model_to_dict(obj) for obj in article_objects]
        df = pd.DataFrame(article_points)
        dic = {}
        for topic, p_id in zip(list(df['p_topic']), list(df['id'])):
            if topic not in dic:
                dic[topic] = []
            dic[topic].append(Point.objects.get(pk=p_id))
        #
        context['sampl_object'] = Point.objects.get(pk=p_id)
        context['article'] = dic
        context['spec'] = source_spec
        context['course'] = course
        context['next'] = next_link
        context['previous'] = previous_link
        return context


class CourseStudyView(
        LoginRequiredMixin,
        CourseSubscriptionRequiredMixin,
        BaseBreadcrumbMixin,
        generic.ListView
        ):
    login_url = 'user:login'
    redirect_field_name = False
    template_name = 'content/coursestudy.html'
    context_object_name = 'context'

    @cached_property
    def crumbs(self):
        return [
                ("content", reverse("content:content")),
                ("course study", '')
            ]

    def get_queryset(self):
        context = {}
        course_id = self.kwargs['course_id']
        #
        course = Course.objects.get(
                    pk=course_id
                )
        latest_course_version = CourseVersion.objects.filter(
                    course=course
                ).order_by('-version_number')[0]
        content = latest_course_version.version_content
        #
        question_history = QuestionTrack.objects.filter(
                user=self.request.user,
                course=course
                ).order_by('-track_creation_time')[:25]
        paper_history = UserPaper.objects.filter(
                user=self.request.user,
                pap_course=course
                ).order_by('pap_creation_time')[:25]
        #
        content = order_live_spec_content(content)
        moduels = OrderedDict({i: moduel for i, moduel in enumerate(content)})
        chapters = collections.defaultdict(list)
        for m_key in moduels:
            chapter_list = [chapter for i, chapter in enumerate(content[moduels[m_key]]['content'])]
            chapters[moduels[m_key]] = chapter_list
        course_subscription = CourseSubscription.objects.filter(
                user=self.request.user,
                course=course
                )
        lesson_quizes = Lesson_quiz.objects.filter(
                user=self.request.user,
                course=course
                ).order_by('-created_at')[:25]
        #
        test_history = sorted(
                chain(lesson_quizes, paper_history),
                key=lambda obj: obj.created_at if hasattr(obj, 'created_at') else obj.pap_creation_time,
                reverse=True
            )
        if self.request.user.is_authenticated:
            if Subscription.objects.filter(customer__id=self.request.user.id, status__in=['trialing', 'active'], livemode=settings.STRIPE_LIVE_MODE).exists():
                context['is_member'] = True
            active_subscriptions = Subscription.objects.filter(customer=self.request.user.id, status__in=['trialing', 'active'], livemode=settings.STRIPE_LIVE_MODE)
            plan_description = str(active_subscriptions[0].plan) if len(active_subscriptions) > 0 else ''
            if 'with ai' in plan_description.lower():
                context['is_AI_member'] = True
        context['coursesubscription'] = course_subscription[0] if len(course_subscription)== 1 else False
        context['content'] = content
        context['moduels'] = moduels
        context['chapters'] = chapters
        context['course'] = course
        context['questionhistory'] = question_history
        context['testhistory'] = test_history
        return context


class CustomTestView(
        CourseSubscriptionRequiredMixin,
        BaseBreadcrumbMixin,
        generic.ListView
        ):
    login_url = 'user:login'
    redirect_field_name = False
    template_name = 'content/customtest.html'
    context_object_name = 'context'

    @cached_property
    def crumbs(self):
        return [
                ("content", reverse("content:content")),
                ("coursestudy", reverse("content:coursestudy", kwargs={'course_id':self.kwargs['course_id']})),
                ("paper", '')
            ]

    def get_queryset(self):
        context = {}
        course_id = self.kwargs['course_id']
        paper_id = self.kwargs['paper_id']
        paper = UserPaper.objects.get(pk=paper_id)
        #
        ordered_paper = []
        paper_questions = list(paper.pap_info.values())
        question_objects = Question.objects.filter(id__in=paper_questions)
        for q in sorted(paper.pap_info.keys()):
            question_id = paper.pap_info[q]
            ordered_paper.append(question_objects.filter(id=question_id)[0])
        #
        question_tracks = QuestionTrack.objects.filter(
                question__in=paper_questions
            )
        all_q_tracks = {q.question.id: q for q in question_tracks}
        #
        context['paper_obj'] = paper
        context['paper'] = ordered_paper
        context['course'] = Course.objects.get(id=course_id)
        context['question_tracks'] = all_q_tracks
        return context


class CourseQuizView(
        CourseSubscriptionRequiredMixin,
        BaseBreadcrumbMixin,
        generic.ListView
        ):
    login_url = 'user:login'
    redirect_field_name = False
    template_name = 'content/coursequiz.html'
    context_object_name = 'context'

    @cached_property
    def crumbs(self):
        return [
                ("content", reverse("content:content")),
                ("coursestudy", reverse("content:coursestudy", kwargs={'course_id':self.kwargs['course_id']})),
                ("quiz", '')
            ]

    def get_queryset(self):
        context = {}
        course_id = self.kwargs['course_id']
        quiz_id = self.kwargs['quiz_id']
        quiz = Lesson_quiz.objects.get(pk=quiz_id)
        #
        solutions = {}
        answers = {}
        for question in quiz.quiz['quiz'].keys():
            solutions[f'{question}'] = quiz.quiz['quiz'][question]['answer']['correct_choice']
            answers[f'{question}'] = quiz.quiz['quiz'][question]['answer']['answer']
        #
        quizzes_states = {}
        questions = {}
        for key in answers.keys():
            user_answer = quiz.user_answers[key] if key in quiz.user_answers.keys() else None
            questions[key] = {
                    "user_answer": user_answer,
                    "correct_choice": solutions[key],
                    "is_correct": True if user_answer == solutions[key] else False,
                    "answer": answers[key],
                }
        quiz_state = {
                "quiz": questions,
                "is_completed": quiz.completed,
                "percentage_score": float(quiz.percentage_score)
            }
        #
        context['quiz'] = quiz
        context['quiz_state'] = quiz_state
        context['course'] = Course.objects.get(id=course_id)
        return context


class PracticeView(
        LoginRequiredMixin,
        BaseBreadcrumbMixin,
        generic.ListView
        ):
    login_url = 'user:login'
    redirect_field_name = False
    template_name = 'content/practice.html'
    context_object_name = 'context'

    @cached_property
    def crumbs(self):
        return [
                ("content", reverse("content:content")),
                ("coursestudy", reverse("content:coursestudy", kwargs={'course_id':self.kwargs['course_id']})),
                ("question", '')
            ]

    def get_queryset(self):
        context = {}
        course_id = self.kwargs['course_id']
        module = self.kwargs['module']
        chapter = self.kwargs['chapter']
        context['title'] = chapter
        #
        course = Course.objects.get(
                    pk=course_id
                )
        content = CourseVersion.objects.filter(
                course=course
            ).order_by('-version_number')[0].version_content
        #
        difficulties = 1
        if self.request.user.is_authenticated:
            if Subscription.objects.filter(customer__id=self.request.user.id, status__in=['trialing', 'active'], livemode=settings.STRIPE_LIVE_MODE).exists():
                difficulties = 5
                context['is_member'] = True
        #
        content = order_live_spec_content(content)
        chapter_qs = content[module]['content'][chapter]['questions']
        dic = OrderedDict()
        all_questions = []
        question = None
        for difficulty in range(difficulties):
            difficulty += 1
            d = str(difficulty)
            if len(chapter_qs[d]) > 0:
                for question in chapter_qs[d]:
                    if d not in dic:
                        dic[d] = []
                    temp_question_object = Question.objects.get(q_unique_id=question)
                    dic[d].append(temp_question_object)
                    all_questions.append(temp_question_object)
        #
        if self.request.user.is_authenticated:
            course_subscription = CourseSubscription.objects.filter(
                    user=self.request.user,
                    course=course
                    )
            if len(course_subscription) > 0:
                course_subscription = course_subscription[0]
                #
                if module not in course_subscription.progress_track.keys():
                    course_subscription.progress_track[module] = {}
                if chapter not in course_subscription.progress_track[module].keys():
                    course_subscription.progress_track[module][chapter] = {}
                if 'questions' not in course_subscription.progress_track[module][chapter].keys():
                    course_subscription.progress_track[module][chapter]['questions'] = True
                course_subscription.save()
                context['coursesubscription'] = course_subscription
                all_q_tracks = {}
                question_tracks = QuestionTrack.objects.filter(
                        user=self.request.user,
                        course=course,
                        question__in=all_questions
                    )
                all_q_tracks = {q.question.id: q for q in question_tracks}
                context['question_tracks'] = all_q_tracks
        context['sampl_object'] = Question.objects.get(q_unique_id=question) if question else None
        context['questions'] = dic if question else None
        context['course'] = course
        context['module'] = module
        context['chapter'] = chapter
        return context


class MarketPlaceView(
            BaseBreadcrumbMixin,
            generic.ListView
        ):

    template_name = "content/marketplace.html"
    context_object_name = 'context'

    @cached_property
    def crumbs(self):
        return [
                ("MarketPlace", '')
                ]

    def get_queryset(self):
        context = {}
        current_page = self.kwargs['page'] if 'page' in self.kwargs else 1
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
        #
        total_learners = CourseSubscription.objects.filter(
                course__in=context['courses']
                ).values('course_id').annotate(count=Count('course'))
        course_sub_counts = {}
        for subscription in total_learners:
            course_sub_counts[int(subscription['course_id'])] = subscription['count']
        for key in context['courses']:
            if key.id not in course_sub_counts.keys():
                course_sub_counts[key.id] = 0
        #
        all_reviews = CourseReview.objects.filter(course__in=context['courses'])
        avg_reviews = all_reviews.values('course_id').annotate(rating=Avg('rating'), count=Count('id'))
        reviews = collections.defaultdict(list)
        for review in avg_reviews:
            reviews[int(subscription['course_id'])] = [review['rating'], review['count']]
        for key in context['courses']:
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


class MarketCourseView(
            BaseBreadcrumbMixin,
            generic.ListView
        ):

    template_name = "content/marketcourse.html"
    context_object_name = 'context'

    @cached_property
    def crumbs(self):
        return [
                ("MarketPlace", reverse("content:marketplace")),
                ("Course", '')
                ]

    def get_queryset(self):
        context = {}
        course_id = self.kwargs['course_id']
        course = Course.objects.get(pk=course_id)
        versions = CourseVersion.objects.filter(course=course).order_by(
                    '-version_number'
                )
        subscription_status = CourseSubscription.objects.filter(
                user=self.request.user,
                course=course
            ).exists() if self.request.user.is_authenticated else False
        #
        total_learners = CourseSubscription.objects.filter(course=course).count()
        all_reviews = CourseReview.objects.filter(course=course)
        avg_reviews = list(all_reviews.aggregate(Avg('rating')).values())[0]
        total_reviews = all_reviews.count()
        content = order_live_spec_content(versions[0].version_content)
        if self.request.user.is_authenticated:
            if Subscription.objects.filter(customer__id=self.request.user.id, status__in=['trialing', 'active'], livemode=settings.STRIPE_LIVE_MODE).exists():
                context['is_member'] = True
            active_subscriptions = Subscription.objects.filter(customer=self.request.user.id, status__in=['trialing', 'active'], livemode=settings.STRIPE_LIVE_MODE)
            plan_description = str(active_subscriptions[0].plan) if len(active_subscriptions) > 0 else ''
            if 'with ai' in plan_description.lower():
                context['is_AI_member'] = True
        context['course'] = course
        context['avg_reviews'] = avg_reviews if avg_reviews else 0.0
        context['total_reviews'] = total_reviews
        context['versions'] = versions
        context['ordered_content'] = content
        context['total_learners'] = total_learners
        context['course_subscription_status'] = subscription_status
        context['CDN_URL'] = settings.CDN_URL
        return context


class CourseReviewsView(
            BaseBreadcrumbMixin,
            generic.ListView
        ):

    template_name = "content/course_reviews.html"
    context_object_name = 'context'

    @cached_property
    def crumbs(self):
        return [
                ("MarketPlace", reverse("content:marketplace")),
                ("Course", reverse("content:marketcourse", kwargs={'course_id':self.kwargs['course_id']})),
                ("Reviews", '')
                ]

    def get_queryset(self):
        context = {}
        course_id = self.kwargs['course_id']
        course = Course.objects.get(pk=course_id)
        reviews = CourseReview.objects.filter(course=course).order_by(
                    '-review_created_at'
                )
        context['course'] = course
        context['reviews'] = reviews
        return context


@login_required(login_url='/user/login', redirect_field_name=None)
def _course_subscribe(request):
    if request.method == 'POST':
        course_id = request.POST['course_id']
        courses = Course.objects.filter(
                pk=course_id
            )
        #
        if len(courses) == 1:
            try:
                course = courses[0]
                CourseSubscription.objects.get_or_create(
                        user=request.user,
                        course=course
                    )
            except Exception:
                messages.add_message(
                        request,
                        messages.INFO,
                        'Something went wrong could not enroll.',
                        extra_tags='alert-warning marketcourse'
                    )
            else:
                messages.add_message(
                        request,
                        messages.INFO,
                        'You have enrolled to this course, goodluck with your studies!',
                        extra_tags='alert-success marketcourse'
                    )
        else:
            messages.add_message(
                    request,
                    messages.INFO,
                    'Something went wrong, could not find course',
                    extra_tags='alert-warning marketcourse'
                )
        #
        return redirect(
                'content:marketcourse', course_id=int(course_id)
            )


@login_required(login_url='/user/login', redirect_field_name=None)
def _new_review(request):
    if request.method == 'POST':
        user = request.user
        course_id = request.POST['course_id']
        course_rating = request.POST['course_rating'] if 'course_rating' in request.POST.keys() else False
        course_review = request.POST['course_review'] if 'course_rating' in request.POST.keys() else False
        #
        course = Course.objects.get(
                pk=course_id
            )
        #
        if course_rating and course_review:
            try:
                review, _= CourseReview.objects.get_or_create(
                        user=request.user,
                        course=course,
                    )
                review.review = course_review
                review.rating = course_rating
                review.save()
            except Exception as e:
                messages.add_message(
                        request,
                        messages.INFO,
                        'Something went wrong, could not create review.',
                        extra_tags='alert-warning marketcourse'
                    )
            else:
                messages.add_message(
                        request,
                        messages.INFO,
                        'Thank you for giving a review.',
                        extra_tags='alert-success marketcourse'
                    )
        else:
            messages.add_message(
                    request,
                    messages.INFO,
                    'Please provide a rating and a review.',
                    extra_tags='alert-danger marketcourse'
                )
        #
        return redirect(
                'content:marketcourse', course_id=int(course_id)
            )


@login_required(login_url='/user/login', redirect_field_name=None)
def _management_options(request):
    if request.method == 'POST':
        subscription_id = h_decode(request.POST['subscription_id'])
        visibility = True if 'subscription_visibility' in request.POST else None
        #
        try:
            subscription = CourseSubscription.objects.get(pk=subscription_id)
        except Exception:
            messages.add_message(
                    request,
                    messages.INFO,
                    'Cannot find the requested course enrollment.',
                    extra_tags='alert-danger contentmanagement'
                )
            return redirect(
                    'dashboard:student_contentmanagement',
                )
        subscription.visibility = visibility
        subscription.save()
        messages.add_message(
                request,
                messages.INFO,
                'Your settings were successfully updated.',
                extra_tags='alert-success contentmanagement'
            )
        return redirect(
                'dashboard:student_contentmanagement',
            )
    return redirect(
            'dashboard:student_contentmanagement',
        )


@AuthorRequiredDec
def _createcourse(request):
    if request.method == 'POST':
        course_type = request.POST['course_type']
        course_name = request.POST['course_name']
        course_level = request.POST['course_level']
        version_name = TagGenerator()
        version_note = 'The course initial version'
        #
        spec_level = request.POST['spec_level']
        spec_subject = request.POST['spec_subject']
        spec_board = 'Universal'
        spec_name = TagGenerator()
        #
        if len(course_name) < 3 and len(version_name) < 3 and \
            len(spec_level) < 3 and len(spec_subject) < 3 and \
            len(spec_board) < 3 and len(version_note) < 3:
            messages.add_message(
                    request,
                    messages.INFO,
                    'Something went wrong could not create course, length of input is too short.',
                    extra_tags='alert-warning course'
                )
            return redirect(
                    'dashboard:mycourses',
                )
        if Specification.objects.filter(
                user=request.user,
                spec_level=spec_level,
                spec_subject=spec_subject,
                spec_board=spec_board,
                spec_name=spec_name,
                ).exists():
            messages.add_message(
                    request,
                    messages.INFO,
                    'A course with similar specifications exists, please make the names are unique.',
                    extra_tags='alert-warning course'
                )
            return redirect(
                    'dashboard:mycourses',
                )

        try:
            spec = Specification.objects.create(
                    user=request.user,
                    spec_level=spec_level,
                    spec_subject=spec_subject,
                    spec_board=spec_board,
                    spec_name=spec_name,
                )
            new_course = Course.objects.create(
                        user=request.user,
                        course_type=course_type,
                        course_name=course_name,
                        course_level=course_level,
                        specification=spec
                    )
            CourseVersion.objects.create(
                        course=new_course,
                        version_number=1,
                        version_name=version_name,
                        version_content=spec.spec_content,
                        version_note=version_note,
                    )
        except Exception as e:
            print(str(e))
            messages.add_message(
                    request,
                    messages.INFO,
                    'Something went wrong could not create course',
                    extra_tags='alert-warning course'
                )
        else:
            messages.add_message(
                    request,
                    messages.INFO,
                    'Your course was created.',
                    extra_tags='alert-success course'
                )
    #
    return redirect(
            'dashboard:mycourses',
        )


@CourseSubscriptionRequiredDec
@AnySubscriptionRequiredDec
def _createcustomtest(request):
    if request.method == 'POST':
        def clean(string):
            string = string.replace('[', '')
            string = string.replace(']', '')
            string = string.replace('"', '')
            string = string.replace(',', ' ')
            return string.split(' ')
        course_id = h_decode(clean(request.POST['course_id'])[0])
        status_array = clean(request.POST['q_status_array'])
        type_array = clean(request.POST['q_type_array'])
        moduel_array = clean(request.POST['q_moduel_array'])
        chapter_array = clean(request.POST['q_chapter_array'])
        difficulty_array = clean(request.POST['q_difficulty_array'])
        # checking for empty filters
        course = Course.objects.get(pk=course_id)
        creator = course.user
        specification = course.specification
        #
        versions = CourseVersion.objects.filter(
            course=course
        ).order_by(
                '-version_number'
            )
        latest_version = versions[0]
        # question pool
        question_list = extract_active_spec_questions(latest_version.version_content)
        question_pool = Question.objects.filter(
                    user=creator,
                    q_unique_id__in=question_list,
                    author_confirmation=True
                )
        try:
            significant_click_name = 'create_custom_test'
            increment_course_subscription_significant_click(
                    request.user, course, significant_click_name
            )
        except Exception as e:
            print(str(e))
        #
        if status_array[0] != '0':
            all_tracked_questions = QuestionTrack.objects.filter(
                    user=request.user,
                    course=course,
                ).values('question__id')
            if 'Seen' in status_array and 'Unseen' in status_array:
                pass
            else:
                if 'Seen' in status_array:
                    question_pool = question_pool.filter(id__in=all_tracked_questions)
                elif 'Unseen' in status_array:
                    question_pool = question_pool.exclude(id__in=all_tracked_questions)
        #
        if type_array[0] != '0':
            allowed_marks = []
            for q_type in type_array:
                if q_type == 'Short':
                    allowed_marks += [1, 2, 3]
                if q_type == 'Medium':
                    allowed_marks += [4, 5, 6, 7]
                if q_type == 'Long':
                    allowed_marks += [i for i in range(8,26,1)]
            #
            if len(allowed_marks) > 0:
                question_pool = question_pool.filter(
                        q_marks__in=allowed_marks
                    )
        if moduel_array[0] != '0':
            question_pool = question_pool.filter(
                    q_moduel__in=moduel_array,
                )
        if chapter_array[0] != '0':
            question_pool = question_pool.filter(
                    q_chapter__in=chapter_array,
                )
        if difficulty_array[0] != '0':
            question_pool = question_pool.filter(
                    q_difficulty__in=difficulty_array,
                )
        final_selection = question_pool[:5]
        paper_content = {i: question.id for i, question in enumerate(final_selection)}
        if len(paper_content) == 5:
            paper = UserPaper.objects.create(
                    user=request.user,
                    pap_course=course,
                    pap_info=paper_content
                )
        else:
            return JsonResponse({'res': 0})
        #
        return JsonResponse({'res': 1, 'course_id': h_encode(course.id), 'paper_id': h_encode(paper.id)})
    else:
        return JsonResponse({'res': 0})


@AuthorRequiredDec
def _updatecourseinformation(request):
    if request.method == 'POST':
        course_id = request.POST['course_id']
        course_name = request.POST['new_name']
        course_upload_image = request.FILES.get("course_thmbnail", None)
        course_level = request.POST['course_level']
        course_description = request.POST['course_description']
        # AI created
        courses = Course.objects.filter(
                user=request.user,
                pk=course_id
            )
        #
        if len(courses) == 1:
            try:
                course = courses[0]
                course.course_name = course_name
                course.course_level = course_level
                course.course_description = course_description
                #
                if course_upload_image:
                    file_name_list = course_upload_image.name.split('.')
                    file_extension = file_name_list.pop(-1)
                    full_name = '.'.join(file_name_list) + '.' + file_extension
                    course.course_pic_ext = full_name
                    request.user.save()
                    if file_extension not in settings.UPLOAD_IMAGE_FORMATS:
                        messages.add_message(
                                request,
                                messages.INFO,
                                'Filetype is not allowed, please user: ' + str(','.join(settings.UPLOAD_IMAGE_FORMATS)),
                                extra_tags='alert-warning course'
                            )
                    else:
                        # save image
                        try:
                            f = BytesIO()
                            for chunk in course_upload_image.chunks():
                                f.write(chunk)
                            f.seek(0)
                            # get object location
                            file_key = f'users/{request.user.id}/courses/{course.id}/course_thumbnail_{full_name}'
                            settings.AWS_S3_C.upload_fileobj(
                                    f,
                                    settings.AWS_BUCKET_NAME,
                                    file_key,
                                    ExtraArgs={'ACL': 'public-read'}
                                )
                            course.course_pic_status = True
                        except Exception as e:
                            messages.add_message(
                                    request,
                                    messages.INFO,
                                    'Could not store your profile image.',
                                    extra_tags='alert-warning course'
                                )
                course.save()
                workflows._generate_outline(course)
            except Exception as e:
                messages.add_message(
                        request,
                        messages.INFO,
                        'Something went wrong could not update course.' + str(e),
                        extra_tags='alert-warning course'
                    )
            else:
                messages.add_message(
                        request,
                        messages.INFO,
                        'Your course was successfully updated.',
                        extra_tags='alert-success course'
                    )
        else:
            messages.add_message(
                    request,
                    messages.INFO,
                    'Something went wrong, could not update course.',
                    extra_tags='alert-warning course'
                )
        #
        return redirect(
                'dashboard:mycourses',
            )


@AuthorRequiredDec
def _deletecourse(request):
    if request.method == 'POST':
        course_id = request.POST['Course_id']
        courses = Course.objects.filter(
                user=request.user,
                pk=h_decode(course_id)
            )
        #
        if len(courses) == 1:
            try:
                course = courses[0]
                course.deleted = True
                course.save()
            except Exception:
                messages.add_message(
                        request,
                        messages.INFO,
                        'Something went wrong could not delete course',
                        extra_tags='alert-warning course'
                    )
            else:
                messages.add_message(
                        request,
                        messages.INFO,
                        'Your course was binned but not permanently deleted.',
                        extra_tags='alert-warning course'
                    )
        else:
            messages.add_message(
                    request,
                    messages.INFO,
                    'Something went wrong, cannot find course.',
                    extra_tags='alert-warning course'
                )
        #
        return redirect(
                'dashboard:mycourses',
            )


@CourseSubscriptionRequiredDec
def _subjective_mark_question(request):
    if request.method == 'POST':
        course_id = request.POST['course_id']
        question_id = request.POST['question_id']
        precieved_difficulty = request.POST['precieved_difficulty']
        course = Course.objects.get(pk=course_id)
        question = Question.objects.get(pk=question_id)
        questiontrack, created = QuestionTrack.objects.get_or_create(
                    user=request.user,
                    course=course,
                    question=question
                )
        #
        try:
            significant_click_name = 'subjective_mark_question'
            increment_course_subscription_significant_click(
                    request.user, course, significant_click_name
            )
        except Exception as e:
            print(str(e))
        try:
            questiontrack.total_marks = question.q_marks
            questiontrack.precieved_difficulty = str(precieved_difficulty)
            questiontrack.save()
            html, video_html, script_html, video_tags = ToMarkdownAnswerManual('', question.id)
            video_button_html = ''
            for vidtag in video_tags:
                video_button_html += f"""
                        <button id='link-{vidtag}' type="button" class="btn btn-primary mb-3"
                            style='display:inline;margin-left:auto;'>
                            <i class="bi bi-caret-right-square-fill"></i>
                        </button>
                """
            if len(video_tags) < 1:
                video_html = False
                script_html = False
                video_button_html = False
            mark_options = ''.join([
                    f"<option value='{mark}'>{mark} Mark(s)</option>"
                    for mark in range(0, question.q_marks + 1, 1)
                ])
            marks_dropdown_html = f"""
                <div
                    class="input-group mb-3"
                    style='width:50%;'
                    id='markingwrapper_{question.id}'
                >
                    <div class="input-group-prepend">
                        <button
                            class='btn btn-primary-outline'
                            style='
                                border: 1px dashed var(--text-color-1);
                                color:var(--text-color-1);
                            '
                            onclick='Controller.C_mark_question("{course.id}","{question.id}")'
                            id='qmarkanswer_{question.id}'
                        >
                            <div id='q_marking_view_{question.id}' class=''>
                                Mark Answer
                            </div>
                            <div id='marking_spinner_and_wait_{question.id}' class='d-none'>
                                <div class="d-flex justify-content-center">
                                  <div class="spinner-border spinner-border-sm" role="status">
                                    <span class="sr-only">Loading...</span>
                                  </div>
                                </div>
                            </div>
                        </button>
                    </div>
                    <select class="custom-select" id="marking_selection_menu_{question.id}">
                        <option selected value='-1'>...</option>
                        {mark_options}
                    </select>
                </div>
            """
            #
            return JsonResponse(
                    {
                        'error': 0,
                        'answer_html': html,
                        'video_html': video_html,
                        'script_html': script_html,
                        'button_html': video_button_html,
                        'marks_dropdown_html': marks_dropdown_html,
                    }
                )
        except Exception as e:
            return JsonResponse({'error': 1, 'message': 'Error'})
    return JsonResponse({'error': 1, 'message': 'Error'})


@CourseSubscriptionRequiredDec
def _mark_question(request):
    if request.method == 'POST':
        course_id = request.POST['course_id']
        question_id = request.POST['question_id']
        n_marks = request.POST['n_marks']
        course = Course.objects.get(pk=course_id)
        question = Question.objects.get(pk=question_id)
        questiontrack, created = QuestionTrack.objects.get_or_create(
                user=request.user,
                course=course,
                question=question
            )
        #
        try:
            significant_click_name = 'mark_question'
            increment_course_subscription_significant_click(
                    request.user, course, significant_click_name
            )
        except Exception as e:
            print(str(e))
        try:
            questiontrack.track_mark = int(n_marks)
            questiontrack.track_attempt_number += 1
            questiontrack.save()
            #
            marking_information = f"""<br>
                Attempt Number: {questiontrack.track_attempt_number} <br>
                Score: {questiontrack.track_mark}/{questiontrack.total_marks};
                    {(questiontrack.track_mark/questiontrack.total_marks)*100}%<br>
            """
            return JsonResponse(
                    {
                        'error': 0,
                        'message': 'Success',
                        'marking_information': marking_information,
                    }
                )
        except Exception as e:
            return JsonResponse({'error': 1, 'message': 'Error'})
    return JsonResponse({'error': 1, 'message': 'Error'})


@CourseSubscriptionRequiredDec
def _mark_paper_question(request):
    if request.method == 'POST':
        #
        course_id = request.POST['course_id']
        paper_id = request.POST['paper_id']
        question_id = request.POST['question_id']
        n_marks = request.POST['n_marks']
        #
        #
        course = Course.objects.get(pk=course_id)
        paper = UserPaper.objects.get(pk=paper_id)
        question = Question.objects.get(pk=question_id)
        questiontrack, created = QuestionTrack.objects.get_or_create(
                user=request.user,
                course=course,
                question=question
            )
        #
        # Add a course subscription month click
        try:
            significant_click_name = 'mark_paper_question'
            increment_course_subscription_significant_click(
                    request.user, course, significant_click_name
            )
        except Exception as e:
            print(str(e))
        #
        inverted_paper = {v: k for k, v in paper.pap_info.items()}
        question_number = inverted_paper[question.id]
        paper_questions = Question.objects.filter(id__in=inverted_paper.keys())
        try:
            questiontrack.track_mark = int(n_marks)
            questiontrack.track_attempt_number += 1
            if question_number not in paper.pap_q_marks:
                paper.pap_q_marks[question_number] = int(n_marks)
            if len(paper.pap_q_marks) == len(inverted_paper):
                paper.pap_completion = True
                #
                total_marks = sum(paper.pap_q_marks.values())
                max_total_marks = sum([q.q_marks for q in paper_questions])
                percentage_score = 0.0
                if max_total_marks > 0:
                    percentage_score = (total_marks / max_total_marks) * 100
                paper.percentage_score = percentage_score
            #
            paper.save()
            questiontrack.save()
            #
            marking_information = f"""<br>
                Attempt Number: {questiontrack.track_attempt_number} <br>
                Score: {questiontrack.track_mark}/{questiontrack.total_marks};
                    {(questiontrack.track_mark/questiontrack.total_marks)*100}%<br>
            """
            return JsonResponse(
                    {
                        'error': 0,
                        'message': 'Success',
                        'marking_information': marking_information,
                    }
                )
        except Exception as e:
            return JsonResponse({'error': 1, 'message': 'Error'})
    return JsonResponse({'error': 1, 'message': 'Error'})


@CourseSubscriptionRequiredDec
def _show_answer(request):
    if request.method == 'POST':
        course_id = request.POST['course_id']
        question_id = request.POST['question_id']
        course = Course.objects.get(pk=course_id)
        question = Question.objects.get(pk=question_id)
        questiontrack, created = QuestionTrack.objects.get_or_create(
                    user=request.user,
                    course=course,
                    question=question
                )
        try:
            html, video_html, script_html, video_tags = ToMarkdownAnswerManual('', question.id)
            video_button_html = ''
            for vidtag in video_tags:
                video_button_html += f"""
                        <button id='link-{vidtag}' type="button" class="btn btn-primary mb-3"
                            style='display:inline;margin-left:auto;'>
                            <i class="bi bi-caret-right-square-fill"></i>
                        </button>
                """
            if len(video_tags) < 1:
                video_html = False
                script_html = False
                video_button_html = False
            # Add the Bootstrap selection menu for marks

            mark_options = ''.join([
                    f"<option value='{mark}'>{mark} Mark(s)</option>"
                    for mark in range(0, question.q_marks + 1, 1)
                ])
            marks_dropdown_html = f"""
                <div
                    class="input-group mb-3"
                    style='width:50%;'
                    id='markingwrapper_{question.id}'
                >
                    <div class="input-group-prepend">
                        <button
                            class='btn btn-primary-outline'
                            style='
                                border: 1px dashed var(--text-color-1);
                                color:var(--text-color-1);
                            '
                            onclick='Controller.C_mark_question("{course.id}","{question.id}")'
                            id='qmarkanswer_{question.id}'
                        >
                            <div id='q_marking_view_{question.id}' class=''>
                                Mark Answer
                            </div>
                            <div id='marking_spinner_and_wait_{question.id}' class='d-none'>
                                <div class="d-flex justify-content-center">
                                  <div class="spinner-border spinner-border-sm" role="status">
                                    <span class="sr-only">Loading...</span>
                                  </div>
                                </div>
                            </div>
                        </button>
                    </div>
                    <select class="custom-select" id="marking_selection_menu_{question.id}">
                        <option selected value='-1'>...</option>
                        {mark_options}
                    </select>
                </div>
            """
            #
            return JsonResponse(
                    {
                        'error': 0,
                        'answer_html': html,
                        'video_html': video_html,
                        'script_html': script_html,
                        'button_html': video_button_html,
                        'marks_dropdown_html': marks_dropdown_html,
                    }
                )
        except Exception as e:
            return JsonResponse({'error': 1, 'message': 'Error'})
    return JsonResponse({'error': 1, 'message': 'Error'})


