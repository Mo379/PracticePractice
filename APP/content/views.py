import datetime
import pandas as pd
import yaml
from django.conf import settings
import collections
from itertools import chain
from collections import OrderedDict
from django.shortcuts import redirect
from django.urls import reverse
from django.http import JsonResponse, HttpResponseRedirect
from django.utils.functional import cached_property
from django.contrib import messages
from django.views import generic
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank
from django.db.models import Count, Avg, F
from content.util.GeneralUtil import (
        TagGenerator,
        ChapterQuestionGenerator,
        insert_new_spec_order,
        order_full_spec_content,
        order_live_spec_content,
        TranslatePointContent,
        TranslateQuestionContent,
        TranslateQuestionAnswer,
        is_valid_youtube_embed,
    )
from view_breadcrumbs import BaseBreadcrumbMixin
from django.forms import model_to_dict
from content.models import *
from content.util.GeneralUtil import increment_course_subscription_significant_click
from content.forms import MDEditorAnswerModleForm, MDEditorQuestionModleForm, MDEditorModleForm
from management.templatetags.general import ToMarkdownAnswerManual
from mdeditor.widgets import MDEditorWidget
from braces.views import (
        LoginRequiredMixin,
        GroupRequiredMixin,
        SuperuserRequiredMixin,
    )
from mdeditor.configs import MDConfig
from io import BytesIO
from PP2.utils import h_encode, h_decode
from AI.tasks import _generate_course_introductions
from AI.models import (
        ContentPromptQuestion,
        ContentPromptTopic,
        ContentPromptPoint,
        Lesson_quiz,
    )
from notification.tasks import _send_email


MDEDITOR_CONFIGS = MDConfig('default')
# Create your views here.


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
                visibility=True
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


class NotesView(
        LoginRequiredMixin,
        BaseBreadcrumbMixin,
        generic.ListView
        ):
    login_url = 'user:login'
    redirect_field_name = False
    template_name = 'content/notes.html'
    context_object_name = 'context'

    @cached_property
    def crumbs(self):
        return [
                ("content", reverse("content:content")),
                ("notes", ''),
                ]

    def get_queryset(self):
        """Return all of the required hub information"""
        context = {}
        course_id = self.kwargs['course_id']
        Note_objs = []
        spec_names = {}
        # optain the subscribed spec or the unviersal spec
        course = Course.objects.get(
                    pk=course_id
                )
        source_spec = course.specification
        content = CourseVersion.objects.filter(
                course=course
            ).order_by('-version_number')[0].version_content
        content = order_full_spec_content(content)
        #
        for key, value in content.items():
            if value['active'] == True:
                for k, v in value['content'].items():
                    if v['active'] == True:
                        Note_objs.append({
                                'p_moduel': key,
                                'p_chapter': k,
                            })
                        spec_names[source_spec.spec_subject] = [source_spec.spec_board,source_spec.spec_name]
        df = pd.DataFrame(Note_objs)
        dic = OrderedDict()
        for m, c in zip(
                list(df['p_moduel']),
                list(df['p_chapter']),
                ):
            if m not in dic:
                dic[m] = []
            dic[m].append(c)
        course_subscription = CourseSubscription.objects.filter(
                user=self.request.user,
                course=course
                )
        context['coursesubscription'] = course_subscription if len(course_subscription) else False
        context['notes'] = dic
        context['spec_names'] = spec_names
        context['course'] = course
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
        content = CourseVersion.objects.filter(
                course=course
            ).order_by('-version_number')[0].version_content
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
        context['coursesubscription'] = course_subscription if len(course_subscription) else False
        context['content'] = content
        context['moduels'] = moduels
        context['chapters'] = chapters
        context['course'] = course
        context['questionhistory'] = question_history
        context['testhistory'] = test_history
        return context


class CustomTestView(
        LoginRequiredMixin,
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
        LoginRequiredMixin,
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
        course_subscription = CourseSubscription.objects.filter(
                user=self.request.user,
                course=course
                )
        content = CourseVersion.objects.filter(
                course=course
            ).order_by('-version_number')[0].version_content
        #
        content = order_live_spec_content(content)
        chapter_qs = content[module]['content'][chapter]['questions']
        dic = OrderedDict()
        all_questions = []
        question = None
        for difficulty in range(5):
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
        all_q_tracks = {}
        question_tracks = QuestionTrack.objects.filter(
                user=self.request.user,
                course=course,
                question__in=all_questions
            )
        all_q_tracks = {q.question.id: q for q in question_tracks}
        context['sampl_object'] = Question.objects.get(q_unique_id=question) if question else None
        context['coursesubscription'] = course_subscription if len(course_subscription) else False
        context['questions'] = dic if question else None
        context['course'] = course
        context['module'] = module
        context['chapter'] = chapter
        context['question_tracks'] = all_q_tracks
        return context


class NoteEditView(
        LoginRequiredMixin,
        BaseBreadcrumbMixin,
        generic.ListView
        ):
    login_url = 'user:login'
    redirect_field_name = False
    template_name = 'content/noteedit.html'
    context_object_name = 'context'

    @cached_property
    def crumbs(self):
        return [
                ]

    def get_queryset(self):
        """Return all of the required hub information"""
        context = {}
        # Get details of page
        spec_id = self.kwargs['spec_id']
        module = self.kwargs['module']
        chapter = self.kwargs['chapter']
        context['title'] = chapter
        #
        source_spec = Specification.objects.get(pk=spec_id)
        #
        content = order_full_spec_content(source_spec.spec_content)
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
        if len(df) > 0:
            for topic, p_id in zip(list(df['p_topic']), list(df['id'])):
                if topic not in dic:
                    dic[topic] = []
                dic[topic].append(Point.objects.get(pk=p_id))
        #
        context['sampl_object'] = {'p_moduel': module, 'p_chapter': chapter}
        context['article'] = dic
        context['spec'] = source_spec
        context['next'] = next_link
        context['previous'] = previous_link
        return context


class QuestionEditView(
        LoginRequiredMixin,
        BaseBreadcrumbMixin,
        generic.ListView
        ):
    login_url = 'user:login'
    redirect_field_name = False
    template_name = 'content/questionedit.html'
    context_object_name = 'context'

    @cached_property
    def crumbs(self):
        return [
            ]

    def get_queryset(self):
        context = {}
        spec_id = self.kwargs['spec_id']
        module = self.kwargs['module']
        chapter = self.kwargs['chapter']
        context['title'] = chapter
        #
        spec = Specification.objects.get(pk=spec_id)
        #
        content = order_full_spec_content(spec.spec_content)
        chapter_qs = content[module]['content'][chapter]['questions']
        dic = OrderedDict()
        question = None
        for difficulty in range(5):
            difficulty += 1
            d = str(difficulty)
            if len(chapter_qs[d]) > 0:
                for question in chapter_qs[d]:
                    if d not in dic:
                        dic[d] = []
                    dic[d].append(Question.objects.get(q_unique_id=question))
                    Question.objects.filter(q_unique_id=question).update(q_subject=spec.spec_subject, q_moduel=module, q_chapter=chapter)
        context['sampl_object'] = Question.objects.get(q_unique_id=question) if question else None
        context['questions'] = dic if question else None
        context['spec'] = spec
        return context


class EditorPointView(
        LoginRequiredMixin,
        BaseBreadcrumbMixin,
        generic.ListView
        ):
    login_url = 'user:login'
    redirect_field_name = False
    template_name = 'content/pointeditor.html'
    context_object_name = 'context'

    @cached_property
    def crumbs(self):
        return [
                ]

    def get_queryset(self):
        """Return all of the required hub information"""
        context = {}
        # Get details of page
        spec_id = self.kwargs['spec_id']
        point_id = self.kwargs['point_id']
        spec = Specification.objects.get(pk=spec_id)
        point = Point.objects.get(pk=point_id)
        translated_content = TranslatePointContent(point.p_content)
        #
        md_config = settings.MDEDITOR_CONFIGS
        toolbar = md_config['default']['toolbar']
        allowed_options = ['|', "video", 'image', '|']
        index_1 = toolbar.index('|')
        index_2 = toolbar.index('|', index_1+1)
        toolbar = toolbar[:index_1] + allowed_options + toolbar[index_2+1:]
        md_config['default']['toolbar'] = toolbar
        editor = MDEditorWidget()
        media = editor.media
        render = editor.render(
                name='p_MDcontent', value=translated_content,
                config=md_config, attrs={'id': 'id_p_MDcontent'}
            )


        context['spec'] = spec
        context['point'] = point
        context['editormedia'] = media
        context['editorrender'] = render
        context['url'] = reverse('content:_savepointedit')
        return context



class EditorQuestionView(
        LoginRequiredMixin,
        BaseBreadcrumbMixin,
        generic.ListView
        ):
    login_url = 'user:login'
    redirect_field_name = False
    template_name = 'content/questioneditor.html'
    context_object_name = 'context'

    @cached_property
    def crumbs(self):
        return [
                ]

    def get_queryset(self):
        """Return all of the required hub information"""
        context = {}
        # Get details of page
        spec_id = self.kwargs['spec_id']
        question_id = self.kwargs['question_id']
        spec = Specification.objects.get(pk=spec_id)
        question = Question.objects.get(pk=question_id)
        #
        translated_content = TranslateQuestionContent(question.q_content)
        translated_answer = TranslateQuestionAnswer(question.q_answer)

        #
        md_config = settings.MDEDITOR_CONFIGS
        toolbar = md_config['default']['toolbar']
        allowed_options = ['|', "video", 'image', '|']
        index_1 = toolbar.index('|')
        index_2 = toolbar.index('|', index_1+1)
        toolbar = toolbar[:index_1] + allowed_options + toolbar[index_2+1:]
        md_config['default']['toolbar'] = toolbar
        editor = MDEditorWidget()
        media = editor.media
        render = editor.render(
                name='q_MDcontent', value=translated_content,
                config=md_config, attrs={'id': 'id_q_MDcontent'}
            )
        a_editor = MDEditorWidget()
        a_media = a_editor.media
        a_render = a_editor.render(
                name='q_MDcontent_ans', value=translated_answer,
                config=md_config, attrs={'id': 'id_q_MDcontent_ans'}
            )

        context['spec'] = spec
        context['question'] = question
        context['editormedia'] = media
        context['editorrender'] = render
        context['editormedia_ans'] = a_media
        context['editorrender_ans'] = a_render
        context['url'] = ''
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


def _publishcourse(request):
    if request.method == 'POST':
        course_id = request.POST['course_id']
        courses = Course.objects.filter(
                user=request.user,
                pk=course_id
            )
        #
        if len(courses) == 1:
            try:
                course = courses[0]
                course.course_publication = True
                course.save()
            except Exception:
                messages.add_message(
                        request,
                        messages.INFO,
                        'Something went wrong could not publish course.',
                        extra_tags='alert-warning course'
                    )
            else:
                messages.add_message(
                        request,
                        messages.INFO,
                        'Your course was successfully published, it can now be found in the CoursePlace.',
                        extra_tags='alert-success course'
                    )
        else:
            messages.add_message(
                    request,
                    messages.INFO,
                    'Something went wrong, could not find course',
                    extra_tags='alert-warning course'
                )
        #
        return redirect(
                'dashboard:mycourses',
            )


def _unpublishcourse(request):
    if request.method == 'POST':
        course_id = request.POST['course_id']
        courses = Course.objects.filter(
                user=request.user,
                pk=course_id
            )
        #
        if len(courses) == 1:
            try:
                course = courses[0]
                course.course_publication = False
                course.save()
            except Exception:
                messages.add_message(
                        request,
                        messages.INFO,
                        'Something went wrong could not unpublish course.',
                        extra_tags='alert-warning course'
                    )
            else:
                messages.add_message(
                        request,
                        messages.INFO,
                        'Your course was successfully unpublished, it will no longer be found in the CoursePlace.',
                        extra_tags='alert-success course'
                    )
        else:
            messages.add_message(
                    request,
                    messages.INFO,
                    'Something went wrong, could not find course',
                    extra_tags='alert-warning course'
                )
        #
        return redirect(
                'dashboard:mycourses',
            )


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
            except Exception as e :
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


def _createcourse(request):
    if request.method == 'POST':
        course_name = request.POST['course_name']
        version_name = request.POST['version_name']
        version_note = request.POST['version_note']
        #
        spec_level = request.POST['spec_level']
        spec_subject = request.POST['spec_subject']
        spec_board = 'Universal'
        spec_name = request.POST['spec_name']
        #
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
                        course_name=course_name,
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
                    'Something went wrong could not create spec',
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


def _createversion(request):
    if request.method == 'POST':
        course_id = request.POST['course_id']
        version_name = request.POST['version_name']
        version_note = request.POST['version_note']
        courses = Course.objects.filter(
                user=request.user,
                pk=course_id
            )
        #
        if len(courses) == 1:
            try:
                versions = CourseVersion.objects.filter(
                            course=courses[0]
                        ).order_by(
                                    '-version_number'
                                )
                latest_version = versions[0]
                CourseVersion.objects.create(
                            course=courses[0],
                            version_number=latest_version.version_number + 1,
                            version_name=version_name,
                            version_content=courses[0].specification.spec_content,
                            version_note=version_note,
                        )
            except Exception as e :
                messages.add_message(
                        request,
                        messages.INFO,
                        'Something went wrong could not create course version.' +str(e),
                        extra_tags='alert-warning course'
                    )
            else:
                messages.add_message(
                        request,
                        messages.INFO,
                        'Your course version was successfully created.',
                        extra_tags='alert-success course'
                    )
        else:
            messages.add_message(
                    request,
                    messages.INFO,
                    'Something went wrong, could not find course.',
                    extra_tags='alert-warning course'
                )
        #
        return redirect(
                'dashboard:mycourses',
            )


def _createmoduel(request):
    if request.method == 'POST':
        level = request.POST['level']
        subject = request.POST['subject']
        board = request.POST['board']
        name = request.POST['name']
        new_module = request.POST['new_module'].replace(' ', '_')
        Template = ContentTemplate.objects.get(
                name='Point'
            )
        #
        points = Point.objects.filter(
                user=request.user,
                p_level=level,
                p_subject=subject,
                p_moduel=new_module,
                erased=False,
            )
        spec = Specification.objects.filter(
                user=request.user,
                spec_level=level,
                spec_subject=subject,
                spec_board=new_module,
                spec_name=name
            )
        if len(points) == 0:
            my_point = Point()
            my_point.user = request.user
            my_point.p_level = level
            my_point.p_subject = subject
            my_point.p_moduel = new_module
            my_point.p_chapter = 'new_chapter'
            my_point.p_topic = 'new_topic'
            my_point.p_number = 1
            my_point.p_title = 'New Point'
            my_point.p_content = Template.content
            my_point.p_unique_id = TagGenerator()
            my_point.save()
            #
            #
            messages.add_message(
                    request,
                    messages.INFO,
                    'Successfully created a new moduel, activate it from the removed list!',
                    extra_tags='alert-success specmoduel'
                )
        else:
            messages.add_message(
                    request,
                    messages.INFO,
                    'Module Already exists, check your removed and binned modules.',
                    extra_tags='alert-success specmoduel'
                )
        kwargs = {
            'level': level,
            'subject': subject,
            'board': board,
            'name': name
        }
        return redirect(
                'dashboard:specmoduel',
                **kwargs
            )


def _createchapter(request):
    if request.method == 'POST':
        level = request.POST['level']
        subject = request.POST['subject']
        module = request.POST['moduel']
        board = request.POST['board']
        name = request.POST['name']
        new_chapter = request.POST['new_chapter'].replace(' ', '_')
        Template = ContentTemplate.objects.get(
                name='Point'
            )
        #
        points = Point.objects.filter(
                user=request.user,
                p_level=level,
                p_subject=subject,
                p_moduel=module,
                p_chapter=new_chapter,
            )
        if len(points) == 0:
            my_point = Point()
            my_point.user = request.user
            my_point.p_level = level
            my_point.p_subject = subject
            my_point.p_moduel = module
            my_point.p_chapter = new_chapter
            my_point.p_topic = 'new_topic'
            my_point.p_number = 1
            my_point.p_title = 'New Point'
            my_point.p_content = Template.content
            my_point.p_unique_id = TagGenerator()
            my_point.save()
            #
            messages.add_message(
                    request,
                    messages.INFO,
                    'Successfully created a new chapter',
                    extra_tags='alert-success specmoduel'
                )
        else:
            messages.add_message(
                    request,
                    messages.INFO,
                    'Chapter Already exists, check your removed or binned chapters.',
                    extra_tags='alert-warning specmoduel'
                )
        kwargs = {
            'level': level,
            'subject': subject,
            'board': board,
            'name': name
        }
        return redirect(
                'dashboard:specmoduel',
                **kwargs
            )


def _createtopic(request):
    if request.method == 'POST':
        level = request.POST['level']
        subject = request.POST['subject']
        board = request.POST['board']
        moduel = request.POST['moduel']
        chapter = request.POST['chapter']
        name = request.POST['name']
        new_topic = request.POST['new_topic'].replace(' ', '_')
        #
        Template = ContentTemplate.objects.get(
                name='Point'
            )
        #
        points = Point.objects.filter(
                user=request.user,
                p_level=level,
                p_subject=subject,
                p_moduel=moduel,
                p_chapter=chapter,
                p_topic=new_topic,
            )
        if len(points) == 0:
            my_point = Point()
            my_point.user = request.user
            my_point.p_level = level
            my_point.p_subject = subject
            my_point.p_moduel = moduel
            my_point.p_chapter = chapter
            my_point.p_topic = new_topic
            my_point.p_number = 1
            my_point.p_title = 'New Point'
            my_point.p_content = Template.content
            my_point.p_unique_id = TagGenerator()
            my_point.save()
            #
            messages.add_message(
                    request,
                    messages.INFO,
                    'Successfully created a new topic',
                    extra_tags='alert-success spectopic'
                )
        else:
            messages.add_message(
                    request,
                    messages.INFO,
                    'Topic Already exists, check your binned topic.',
                    extra_tags='alert-warning spectopic'
                )
        kwargs = {
            'level': level,
            'subject': subject,
            'board': board,
            'module': moduel,
            'chapter': chapter,
            'name': name
        }
        return redirect(
                'dashboard:spectopic',
                **kwargs
            )


def _createpoint(request):
    if request.method == 'POST':
        level = request.POST['level']
        subject = request.POST['subject']
        board = request.POST['board']
        moduel = request.POST['moduel']
        chapter = request.POST['chapter']
        topic = request.POST['topic']
        name = request.POST['name'].replace(' ', '_')
        new_point = request.POST['new_point']
        #
        Template = ContentTemplate.objects.get(
                name='Point'
            )
        #
        points = Point.objects.filter(
                user=request.user,
                p_level=level,
                p_subject=subject,
                p_moduel=moduel,
                p_chapter=chapter,
                p_topic=topic,
            )
        my_point = Point()
        if len(points) == 0:
            my_point.p_number = 1
        else:
            my_point.p_number = len(points) + 1
        my_point.user = request.user
        my_point.p_level = level
        my_point.p_subject = subject
        my_point.p_moduel = moduel
        my_point.p_chapter = chapter
        my_point.p_topic = topic
        my_point.p_title = name
        my_point.p_content = Template.content
        my_point.p_unique_id = TagGenerator()
        my_point.save()
        #
        messages.add_message(
                request,
                messages.INFO,
                'Successfully created a new point',
                extra_tags='alert-success spectopic'
            )
        kwargs = {
            'level': level,
            'subject': subject,
            'board': board,
            'module': moduel,
            'chapter': chapter,
            'board': board,
            'name': name
        }
        return redirect(
                'dashboard:spectopic',
                **kwargs
            )


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
        # question pool
        question_pool = Question.objects.filter(
                    user=creator,
                    q_subject=specification.spec_subject,
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


def _updatecourseinformation(request):
    if request.method == 'POST':
        course_id = request.POST['course_id']
        course_name = request.POST['new_name']
        course_upload_image = request.FILES.get("course_thmbnail", None)
        course_level = request.POST['course_level']
        regenerate_summary = True if 'regenerate_summary' in request.POST else None
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
                #
                if regenerate_summary:
                    course.course_skills = {idd: '(AI is working...)' for idd in range(6)}
                    course.course_summary = '(AI is working...)'
                    course.course_learning_objectives = {idd: '(AI is working...)' for idd in range(6)}
                    course.course_publication = False
                #
                # Upload image
                if course_upload_image:
                    file_name_list = course_upload_image.name.split('.')
                    file_extension = file_name_list.pop(-1)
                    full_name = '.'.join(file_name_list) + '.' + file_extension
                    course.course_pic_ext = full_name
                    request.user.save()
                    if file_extension not in MDEDITOR_CONFIGS['upload_image_formats']:
                        messages.add_message(
                                request,
                                messages.INFO,
                                'Filetype is not allowed, please user: ' + str(','.join(MDEDITOR_CONFIGS['upload_image_formats'])),
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
                if regenerate_summary:
                    _generate_course_introductions.delay(request.user.id, course.id)
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


def _updatepointvideos(request):
    if request.method == 'POST':
        point_id = request.POST['point_id']
        point = Point.objects.filter(user=request.user, pk=point_id)
        videos_list = request.POST.getlist('ordered_items_videos[]')
        if len(point) == 1:
            try:
                point[0].p_videos.clear()
                for vid in videos_list:
                    title = vid.split('<sep>')[0]
                    url = vid.split('<sep>')[1]
                    if is_valid_youtube_embed(url) == False:
                        return JsonResponse({'error': 1, 'message': f'Invalid link'})

                    if Video.objects.filter(user=request.user,url=url).exists():
                        video = Video.objects.filter(
                                user=request.user,
                                url=url,
                            )[0]
                    else:
                        video = Video.objects.create(user=request.user, url=url)
                    video.title = title
                    video.save()
                    point[0].p_videos.add(video)
                point[0].save()
                return JsonResponse({'error': 0, 'message': 'Saved'})
            except Exception as e:
                return JsonResponse({'error': 1, 'message': f'Error {str(e)}'})
        return JsonResponse({'error': 1, 'message': 'Error b'})
    return JsonResponse({'error': 1, 'message': 'Error c'})


def _updatequestionvideos(request):
    if request.method == 'POST':
        question_id = request.POST['question_id']
        question = Question.objects.filter(user=request.user, pk=question_id)
        videos_list = request.POST.getlist('ordered_items_videos[]')
        if len(question) == 1:
            try:
                for vid in videos_list:
                    url = vid.split('<sep>')[2]
                    if is_valid_youtube_embed(url) == False:
                        return JsonResponse({'error': 1, 'message': f'Invalid link'})
                question[0].q_videos.clear()
                for vid in videos_list:
                    placement = vid.split('<sep>')[0]
                    title = vid.split('<sep>')[1]
                    url = vid.split('<sep>')[2]
                    if Video.objects.filter(user=request.user,url=url).exists():
                        video = Video.objects.filter(
                                user=request.user,
                                url=url,
                            )[0]
                    else:
                        video = Video.objects.create(user=request.user, url=url)
                    video.in_question_placement = False if placement.lower() == 'answer' else True
                    video.title = title
                    video.save()
                    question[0].q_videos.add(video)
                question[0].save()
                return JsonResponse({'error': 0, 'message': 'Saved'})
            except Exception as e:
                return JsonResponse({'error': 1, 'message': f'Error {str(e)}'})
        return JsonResponse({'error': 1, 'message': 'Error b'})
    return JsonResponse({'error': 1, 'message': 'Error c'})


def _updatepointimages(request):
    if request.method == 'POST':
        point_id = request.POST['point_id']
        point = Point.objects.filter(user=request.user, pk=point_id)
        images_information = request.POST.getlist('ordered_items_images[]')
        if len(point) == 1:
            try:
                point[0].p_images.clear()
                for image_info in images_information:
                    parts = image_info.split('<sep>')
                    image_description = parts[0]
                    image_id = parts[1]
                    #
                    image_obj = Image.objects.get(pk=image_id)
                    image_obj.description = image_description
                    image_obj.save()
                    point[0].p_images.add(image_obj)
                return JsonResponse({'error': 0, 'message': 'Saved'})
            except Exception as e:
                return JsonResponse({'error': 1, 'message': 'Error'+str(e)})
        return JsonResponse({'error': 1, 'message': 'Error'})
    return JsonResponse({'error': 1, 'message': 'Error'})


def _updatequestionimages(request):
    if request.method == 'POST':
        question_id = request.POST['question_id']
        question = Question.objects.filter(user=request.user, pk=question_id)
        images_information = request.POST.getlist('ordered_items_images[]')
        if len(question) == 1:
            try:
                question[0].q_images.clear()
                active_images = []
                for image_info in images_information:
                    parts = image_info.split('<sep>')
                    image_description = parts[0]
                    image_id = parts[1]
                    image_placement = parts[2]
                    #
                    image_obj = Image.objects.get(pk=image_id)
                    image_obj.description = image_description
                    image_obj.in_question_placement = image_placement
                    image_obj.save()
                    question[0].q_images.add(image_obj)
                return JsonResponse({'error': 0, 'message': 'Saved'})
            except Exception as e:
                return JsonResponse({'error': 1, 'message': 'Error'+str(e)})
        return JsonResponse({'error': 1, 'message': 'Error'})
    return JsonResponse({'error': 1, 'message': 'Error'})


def _uploadquestionimage(request):
    if request.method == 'POST':
        question_id = request.POST['question_id']
        image_placement = request.POST.get('image_placement')
        image_description = request.POST.get('image_desciption')
        upload_image = request.FILES.get("image_file", None)
        q_placement = True if image_placement else False
        # image none check
        if not upload_image:
            return JsonResponse({
                'error': 1,
                'message': "Failed to find an image.",
            })
        # image format check
        upload_image.name = upload_image.name.replace('_', '')
        file_name_list = upload_image.name.split('.')
        file_extension = file_name_list.pop(-1)
        file_name = '.'.join(file_name_list)
        if file_extension not in MDEDITOR_CONFIGS['upload_image_formats']:
            return JsonResponse({
                'error': 1,
                'message': "Invalid format detected, image has got to be：%s" % ','.join(
                    MDEDITOR_CONFIGS['upload_image_formats']),
            })
        # save image
        try:
            f = BytesIO()
            for chunk in upload_image.chunks():
                f.write(chunk)
            f.seek(0)
            obj = Question.objects.get(pk=question_id)
            file_key = f'universal/question_{obj.id}_{file_name}.{file_extension}'
            image_obj = Image.objects.create(
                    user=request.user,
                    description=image_description,
                    url=file_key,
                    in_question_placement=q_placement,
                )
            obj.q_images.add(image_obj)
            settings.AWS_S3_C.upload_fileobj(
                    f,
                    settings.AWS_BUCKET_NAME,
                    file_key,
                    ExtraArgs={'ACL': 'public-read'}
                )
        except Exception as e:
            return JsonResponse({
                'error': 1,
                'message': 'Something went wrong cannot upload image.',
            })
        else:
            # image floder check
            return JsonResponse({'error': 0,
                                 'message': "File uploaded!",
                                 })
def _uploadpointimage(request):
    if request.method == 'POST':
        point_id = request.POST['point_id']
        image_description = request.POST.get('image_desciption')
        upload_image = request.FILES.get("image_file", None)
        # image none check
        if not upload_image:
            return JsonResponse({
                'error': 1,
                'message': "Failed to find an image.",
            })
        # image format check
        upload_image.name = upload_image.name.replace('_', '')
        file_name_list = upload_image.name.split('.')
        file_extension = file_name_list.pop(-1)
        file_name = '.'.join(file_name_list)
        if file_extension not in MDEDITOR_CONFIGS['upload_image_formats']:
            return JsonResponse({
                'error': 1,
                'message': "Invalid format detected, image has got to be：%s" % ','.join(
                    MDEDITOR_CONFIGS['upload_image_formats']),
            })
        # save image
        try:
            f = BytesIO()
            for chunk in upload_image.chunks():
                f.write(chunk)
            f.seek(0)
            obj = Point.objects.get(pk=point_id)
            file_key = f'universal/point_{obj.id}_{file_name}.{file_extension}'
            image_obj = Image.objects.create(
                    user=request.user,
                    description=image_description,
                    url=file_key,
                )
            obj.p_images.add(image_obj)
            settings.AWS_S3_C.upload_fileobj(
                    f,
                    settings.AWS_BUCKET_NAME,
                    file_key,
                    ExtraArgs={'ACL': 'public-read'}
                )
        except Exception as e:
            return JsonResponse({
                'error': 1,
                'message': 'Something went wrong cannot upload image.',
            })
        else:
            # image floder check
            return JsonResponse({'error': 0,
                                 'message': "File uploaded!",
                                 })
def _renamespec(request):
    if request.method == 'POST':
        level = request.POST['level']
        subject = request.POST['subject']
        board = request.POST['board']
        name = request.POST['name']
        new_name = request.POST['new_name']
        #
        specs = Specification.objects.filter(
                user=request.user,
                spec_level=level,
                spec_subject=subject,
                spec_board=board,
                spec_name=name,
            )
        if new_name.isalnum():
            if len(specs) == 1:
                spec = specs[0]
                spec.spec_name = new_name
                spec.save()
                messages.add_message(
                        request,
                        messages.INFO,
                        'Specification Was Renamed',
                        extra_tags='alert-success specmoduel'
                    )
            else:
                messages.add_message(
                        request,
                        messages.INFO,
                        'Something went wrong, spec isnt unique.',
                        extra_tags='alert-warning specmoduel'
                    )
        else:
            messages.add_message(
                    request,
                    messages.INFO,
                    'Input can only be alphaneumeric.',
                    extra_tags='alert-warning specmoduel'
                )
            kwargs = {
                'level': level,
                'subject': subject,
                'board': board,
                'name': name,
            }
            return redirect(
                    'dashboard:specmoduel',
                    **kwargs
                )
        kwargs = {
            'level': level,
            'subject': subject,
            'board': board,
            'name': new_name,
        }
        return redirect(
                'dashboard:specmoduel',
                **kwargs
            )


def _renamemodule(request):
    if request.method == 'POST':
        level = request.POST['level']
        subject = request.POST['subject']
        module = request.POST['moduel']
        board = request.POST['board']
        name = request.POST['name']
        new_name = request.POST['new_name'].replace(' ', '_')
        points = Point.objects.filter(
                user=request.user,
                p_level=level,
                p_subject=subject,
                p_moduel=module
            )
        questions = Question.objects.filter(
                user=request.user,
                q_subject=subject,
                q_moduel=module
            )
        spec = Specification.objects.get(
                user=request.user,
                spec_level=level,
                spec_subject=subject,
                spec_board=board,
                spec_name=name,
            )
        q_prmpts = ContentPromptQuestion.objects.filter(
                user=request.user,
                specification=spec,
                moduel=module
                )
        t_prmpts = ContentPromptTopic.objects.filter(
                user=request.user,
                specification=spec,
                moduel=module
                )
        p_prmpts = ContentPromptPoint.objects.filter(
                user=request.user,
                specification=spec,
                moduel=module
                )
        if len(points) > 0:
            points.update(p_moduel=new_name)
            questions.update(q_moduel=new_name)
            q_prmpts.update(moduel=new_name)
            t_prmpts.update(moduel=new_name)
            p_prmpts.update(moduel=new_name)
            # change spec info
            content = spec.spec_content.copy()
            if module in content.keys():
                content[new_name] = content.pop(module)
                spec.spec_content = content
                spec.save()
            messages.add_message(
                    request,
                    messages.INFO,
                    f'Successfully Renamed the moduel: {module} -> {new_name}',
                    extra_tags='alert-warning specmoduel'
                )
        else:
            messages.add_message(
                    request,
                    messages.INFO,
                    'Something is wrong, please check that the input is correct.',
                    extra_tags='alert-warning specmoduel'
                )
        kwargs = {
            'level': level,
            'subject': subject,
            'board': board,
            'name': name,
        }
        return redirect(
                'dashboard:specmoduel',
                **kwargs
            )


def _renamechapter(request):
    if request.method == 'POST':
        level = request.POST['level']
        subject = request.POST['subject']
        module = request.POST['moduel']
        chapter = request.POST['chapter']
        board = request.POST['board']
        name = request.POST['name']
        new_name = request.POST['new_name'].replace(' ', '_')
        #
        points = Point.objects.filter(
                user=request.user,
                p_level=level,
                p_subject=subject,
                p_moduel=module,
                p_chapter=chapter,
            )
        questions = Question.objects.filter(
                user=request.user,
                q_subject=subject,
                q_moduel=module,
                q_chapter=chapter,
            )
        spec = Specification.objects.get(
                user=request.user,
                spec_level=level,
                spec_subject=subject,
                spec_board=board,
                spec_name=name,
            )
        q_prmpts = ContentPromptQuestion.objects.filter(
                user=request.user,
                specification=spec,
                moduel=module,
                chapter=chapter,
                )
        t_prmpts = ContentPromptTopic.objects.filter(
                user=request.user,
                specification=spec,
                moduel=module,
                chapter=chapter,
                )
        p_prmpts = ContentPromptPoint.objects.filter(
                user=request.user,
                specification=spec,
                moduel=module,
                chapter=chapter,
                )
        if len(points) > 0:
            points.update(p_chapter=new_name)
            questions.update(q_chapter=new_name)
            q_prmpts.update(chapter=new_name)
            t_prmpts.update(chapter=new_name)
            p_prmpts.update(chapter=new_name)
            # change spec info
            content = spec.spec_content.copy()
            if module in content.keys():
                if chapter in content[module]['content'].keys():
                    content[module]['content'][new_name] = content[module]['content'].pop(chapter)
                    spec.spec_content = content
                    spec.save()
            messages.add_message(
                    request,
                    messages.INFO,
                    f'Successfully Renamed the chapter: {chapter} -> {new_name}',
                    extra_tags='alert-warning specmoduel'
                )
        else:
            messages.add_message(
                    request,
                    messages.INFO,
                    'Something is wrong, please check that the input is correct.',
                    extra_tags='alert-warning specmoduel'
            )
            kwargs = {
                'level': level,
                'subject': subject,
                'board': board,
                'name': name,
            }
            return redirect(
                    'dashboard:specmoduel',
                    **kwargs
                )
        kwargs = {
            'level': level,
            'subject': subject,
            'board': board,
            'name': name,
        }
        return redirect(
                'dashboard:specmoduel',
                **kwargs
            )


def _renametopic(request):
    if request.method == 'POST':
        level = request.POST['level']
        subject = request.POST['subject']
        module = request.POST['moduel']
        chapter = request.POST['chapter']
        topic = request.POST['topic']
        board = request.POST['board']
        name = request.POST['name']
        new_name = request.POST['new_name'].replace(' ', '_')
        #
        points = Point.objects.filter(
                user=request.user,
                p_level=level,
                p_subject=subject,
                p_moduel=module,
                p_chapter=chapter,
                p_topic=topic,
            )
        spec = Specification.objects.get(
                user=request.user,
                spec_level=level,
                spec_subject=subject,
                spec_board=board,
                spec_name=name,
            )
        t_prmpts = ContentPromptTopic.objects.filter(
                user=request.user,
                specification=spec,
                moduel=module,
                chapter=chapter,
                topic=topic,
                )
        p_prmpts = ContentPromptPoint.objects.filter(
                user=request.user,
                specification=spec,
                moduel=module,
                chapter=chapter,
                topic=topic,
                )
        if len(points) > 0:
            points.update(p_topic=new_name)
            t_prmpts.update(topic=new_name)
            p_prmpts.update(topic=new_name)
            # change spec info
            content = spec.spec_content.copy()
            if module in content.keys():
                if chapter in content[module]['content'].keys():
                    if topic in content[module]['content'][chapter]['content'].keys():
                        content[module]['content'][chapter]['content'][new_name] = content[module]['content'][chapter]['content'].pop(topic)
                        spec.spec_content = content
                        spec.save()
            messages.add_message(
                    request,
                    messages.INFO,
                    f'Successfully Renamed the topic: {topic} -> {new_name}',
                    extra_tags='alert-warning spectopic'
                )
        else:
            messages.add_message(
                    request,
                    messages.INFO,
                    'Something is wrong, please check that the input is correct.',
                    extra_tags='alert-warning spectopic'
            )
            kwargs = {
                'level': level,
                'subject': subject,
                'module': module,
                'chapter': chapter,
                'board': board,
                'name': name,
            }
            return redirect(
                    'dashboard:spectopic',
                    **kwargs
                )
        kwargs = {
            'level': level,
            'subject': subject,
            'module': module,
            'chapter': chapter,
            'board': board,
            'name': name,
        }
        return redirect(
                'dashboard:spectopic',
                **kwargs
            )


def _renamepoint(request):
    if request.method == 'POST':
        level = request.POST['level']
        subject = request.POST['subject']
        module = request.POST['moduel']
        chapter = request.POST['chapter']
        board = request.POST['board']
        name = request.POST['name']
        #
        point_id = request.POST['p_id']
        title = request.POST['new_name'].replace(' ', '_')
        #
        points = Point.objects.filter(
                user=request.user,
                p_unique_id=point_id
            )
        if len(points) > 0:
            points[0].p_title = title
            points[0].save()
            messages.add_message(
                    request,
                    messages.INFO,
                    f'Successfully Renamed the point.',
                    extra_tags='alert-warning spectopic'
                )
        else:
            messages.add_message(
                    request,
                    messages.INFO,
                    'Something is wrong, please check that the input is correct.',
                    extra_tags='alert-warning spectopic'
            )
            kwargs = {
                'level': level,
                'subject': subject,
                'module': module,
                'chapter': chapter,
                'board': board,
                'name': name,
            }
            return redirect(
                    'dashboard:spectopic',
                    **kwargs
                )
        kwargs = {
            'level': level,
            'subject': subject,
            'module': module,
            'chapter': chapter,
            'board': board,
            'name': name,
        }
        return redirect(
                'dashboard:spectopic',
                **kwargs
            )


def _ordermoduels(request):
    if request.method == 'POST':
        spec_id = request.POST.getlist('spec_id')
        ordered_moduels = request.POST.getlist('order')[0].split(',')
        # Get objects
        spec = Specification.objects.get(
                user=request.user,
                pk=int(spec_id[0])
            )
        content = spec.spec_content.copy()
        new_information = insert_new_spec_order(ordered_moduels, content, 'moduel')
        content = new_information
        # Update the values
        spec.spec_content = content
        spec.save()
        return JsonResponse({'error': 0, 'message': 'Saved'})
    return JsonResponse({'error': 1, 'message': 'Error'})


def _orderchapters(request):
    if request.method == 'POST':
        spec_id = request.POST['spec_id']
        module = request.POST['module']
        ordered_chapters = request.POST.getlist('order')[0].split(',')
        # Get objects
        spec = Specification.objects.get(
                user=request.user,
                pk=int(spec_id)
            )
        content = spec.spec_content.copy()
        new_information = insert_new_spec_order(
                ordered_chapters,
                content[module]['content'],
                'chapter'
            )
        content[module]['content'] = new_information
        # Check and insert questions
        module_content = ChapterQuestionGenerator(
                request.user,
                spec.spec_subject,
                module,
                content[module]['content'].copy()
            )
        content[module]['content'] = module_content
        #
        spec.spec_content = content
        spec.save()
        return JsonResponse({'error': 0, 'message': 'Saved'})
    return JsonResponse({'error': 1, 'message': 'Error'})


def _ordertopics(request):
    if request.method == 'POST':
        spec_id = request.POST['spec_id']
        moduel = request.POST['module']
        chapter = request.POST['chapter']
        ordered_topics = request.POST.getlist('order')[0].split(',')
        # Get objects
        spec = Specification.objects.get(
                user=request.user,
                pk=spec_id
            )
        content = spec.spec_content.copy()
        new_information = insert_new_spec_order(
                ordered_topics,
                content[moduel]['content'][chapter]['content'],
                'topic'
            )
        content[moduel]['content'][chapter]['content'] = new_information
        spec.spec_content = content
        spec.save()
        return JsonResponse({'error': 0, 'message': 'Saved'})
    return JsonResponse({'error': 1, 'message': 'Error'})


def _orderpoints(request):
    if request.method == 'POST':
        spec_id = request.POST['spec_id']
        moduel = request.POST['module']
        chapter = request.POST['chapter']
        topic = request.POST['topic']
        ordered_topics = request.POST.getlist('order')[0].split(',')
        # Get objects
        spec = Specification.objects.get(
                user=request.user,
                pk=spec_id
            )
        content = spec.spec_content.copy()
        new_information = insert_new_spec_order(
                ordered_topics,
                content[moduel]['content'][chapter]['content'][topic]['content'],
                'point'
            )
        content[moduel]['content'][chapter]['content'][topic]['content'] = new_information
        content = order_full_spec_content(content)
        spec.spec_content = content
        spec.save()
        return JsonResponse({'error': 0, 'message': 'Saved'})
    return JsonResponse({'error': 1, 'message': 'Error'})


def _removemodule(request):
    if request.method == 'POST':
        spec_id = request.POST['spec_id']
        module = request.POST['module']
        # Get objects
        spec = Specification.objects.get(
                user=request.user,
                pk=int(spec_id)
            )
        content = spec.spec_content.copy()
        content[module]['active'] = False
        content[module]['position'] = -1
        # Update the values
        spec.spec_content = content
        spec.save()
        return JsonResponse({'error': 0, 'message': 'Saved'})
    return JsonResponse({'error': 1, 'message': 'Error'})


def _removechapter(request):
    if request.method == 'POST':
        spec_id = request.POST['spec_id']
        module = request.POST['module']
        chapter = request.POST['chapter']
        # Get objects
        spec = Specification.objects.get(
                user=request.user,
                pk=int(spec_id)
            )
        content = spec.spec_content.copy()
        content[module]['content'][chapter]['active'] = False
        content[module]['content'][chapter]['position'] = -1
        # Update the values
        spec.spec_content = content
        spec.save()
        return JsonResponse({'error': 0, 'message': 'Saved'})
    return JsonResponse({'error': 1, 'message': 'Error'})


def _removetopic(request):
    if request.method == 'POST':
        spec_id = request.POST['spec_id']
        module = request.POST['module']
        chapter = request.POST['chapter']
        topic = request.POST['topic']
        # Get objects
        spec = Specification.objects.get(
                user=request.user,
                pk=int(spec_id)
            )
        content = spec.spec_content.copy()
        content[module]['content'][chapter]['content'][topic]['active'] = False
        content[module]['content'][chapter]['content'][topic]['position'] = -1
        # Update the values
        spec.spec_content = content
        spec.save()
        return JsonResponse({'error': 0, 'message': 'Saved'})
    return JsonResponse({'error': 1, 'message': 'Error'})


def _removepoint(request):
    if request.method == 'POST':
        spec_id = request.POST['spec_id']
        module = request.POST['module']
        chapter = request.POST['chapter']
        topic = request.POST['topic']
        point = request.POST['point']
        # Get objects
        spec = Specification.objects.get(
                user=request.user,
                pk=int(spec_id)
            )
        content = spec.spec_content.copy()
        content[module]['content'][chapter]['content'][topic]['content'][point]['active'] = False
        content[module]['content'][chapter]['content'][topic]['content'][point]['position'] = -1
        # Update the values
        spec.spec_content = content
        spec.save()
        return JsonResponse({'error': 0, 'message': 'Saved'})
    return JsonResponse({'error': 1, 'message': 'Error'})


def _restoremodule(request):
    if request.method == 'POST':
        spec_id = request.POST['spec_id']
        module = request.POST['module']
        # Get objects
        spec = Specification.objects.get(
                user=request.user,
                pk=int(spec_id)
            )
        content = spec.spec_content.copy()
        if module in content.keys():
            save_content = content[module]['content']
        else:
            save_content = {}
        # Update the values
        ordered_moduels = list(order_live_spec_content(content).keys())
        ordered_moduels = [module] + ordered_moduels
        new_information = insert_new_spec_order(ordered_moduels, content, 'moduel')
        new_information[module]['content'] = save_content
        # Update the values
        spec.spec_content = new_information
        spec.save()
        return JsonResponse({'error': 0, 'message': 'Saved'})
    return JsonResponse({'error': 1, 'message': 'Error'})


def _restorechapter(request):
    if request.method == 'POST':
        spec_id = request.POST['spec_id']
        module = request.POST['module']
        chapter = request.POST['chapter']
        # Get objects
        spec = Specification.objects.get(
                user=request.user,
                pk=int(spec_id)
            )
        content = spec.spec_content.copy()
        if chapter in content[module]['content'].keys():
            save_content = content[module]['content'][chapter]['content']
        else:
            save_content = {}
        # Update the values
        ordered_chapters = list(order_live_spec_content(content)[module]['content'].keys())
        ordered_chapters = [chapter] + ordered_chapters
        new_information = insert_new_spec_order(ordered_chapters, content[module]['content'], 'chapter')
        new_information[chapter]['content'] = save_content
        # Update the values
        content[module]['content'] = new_information
        # Check and insert questions
        module_content = ChapterQuestionGenerator(
                request.user,
                spec.spec_subject,
                module,
                content[module]['content'].copy()
            )
        content[module]['content'] = module_content
        spec.spec_content = content
        spec.save()
        return JsonResponse({'error': 0, 'message': 'Saved'})
    return JsonResponse({'error': 1, 'message': 'Error'})


def _restoretopic(request):
    if request.method == 'POST':
        spec_id = request.POST['spec_id']
        module = request.POST['module']
        chapter = request.POST['chapter']
        topic = request.POST['topic']
        # Get objects
        spec = Specification.objects.get(
                user=request.user,
                pk=int(spec_id)
            )
        content = spec.spec_content.copy()
        if topic in content[module]['content'][chapter]['content'].keys():
            save_content = content[module]['content'][chapter]['content'][topic]['content']
        else:
            save_content = {}
        # Update the values
        ordered_topics = list(order_live_spec_content(content)[module]['content'][chapter]['content'].keys())
        ordered_topics = [topic] + ordered_topics
        new_information = insert_new_spec_order(ordered_topics, content[module]['content'][chapter]['content'], 'topic')
        # Update the values
        new_information[topic]['content'] = save_content
        content[module]['content'][chapter]['content'] = new_information
        spec.spec_content = content
        spec.save()
        return JsonResponse({'error': 0, 'message': 'Saved'})
    return JsonResponse({'error': 1, 'message': 'Error'})


def _restorepoint(request):
    if request.method == 'POST':
        spec_id = request.POST['spec_id']
        module = request.POST['module']
        chapter = request.POST['chapter']
        topic = request.POST['topic']
        point = request.POST['point']
        # Get objects
        spec = Specification.objects.get(
                user=request.user,
                pk=int(spec_id)
            )
        content = spec.spec_content.copy()
        # Update the values
        ordered_points = list(order_live_spec_content(content)[module]['content'][chapter]['content'][topic]['content'].keys())
        ordered_points = [point] + ordered_points
        new_information = insert_new_spec_order(ordered_points, content[module]['content'][chapter]['content'][topic]['content'], 'point')
        # Update the values
        content[module]['content'][chapter]['content'][topic]['content'] = new_information
        spec.spec_content = content
        spec.save()
        return JsonResponse({'error': 0, 'message': 'Saved'})
    return JsonResponse({'error': 1, 'message': 'Error'})


def _undeletemodule(request):
    if request.method == 'POST':
        spec_id = request.POST['spec_id']
        module = request.POST['module']
        # Get objects
        spec = Specification.objects.get(
                user=request.user,
                pk=int(spec_id)
            )
        points = Point.objects.filter(
                user=request.user,
                p_level=spec.spec_level,
                p_subject=spec.spec_subject,
                p_moduel__iexact=module,
            )
        points.update(deleted=False)
        content = spec.spec_content.copy()
        if module in content.keys():
            save_content = content[module]['content']
        else:
            save_content = {}
        # Update the values
        ordered_moduels = list(order_live_spec_content(content).keys())
        ordered_moduels = [module] + ordered_moduels
        new_information = insert_new_spec_order(ordered_moduels, content, 'moduel')
        new_information[module]['content'] = save_content
        # Update the values
        spec.spec_content = new_information
        spec.save()
        return JsonResponse({'error': 0, 'message': 'Saved'})
    return JsonResponse({'error': 1, 'message': 'Error'})


def _undeletechapter(request):
    if request.method == 'POST':
        spec_id = request.POST['spec_id']
        module = request.POST['module']
        chapter = request.POST['chapter']
        # Get objects
        spec = Specification.objects.get(
                user=request.user,
                pk=int(spec_id)
            )
        points = Point.objects.filter(
                user=request.user,
                p_level=spec.spec_level,
                p_subject=spec.spec_subject,
                p_moduel__iexact=module,
                p_chapter__iexact=chapter,
            )
        points.update(deleted=False)
        content = spec.spec_content.copy()
        if chapter in content[module]['content'].keys():
            save_content = content[module]['content'][chapter]['content']
        else:
            save_content = {}
        # Update the values
        ordered_chapters = list(order_live_spec_content(content)[module]['content'].keys())
        ordered_chapters = [chapter] + ordered_chapters
        new_information = insert_new_spec_order(ordered_chapters, content[module]['content'], 'chapter')
        new_information[chapter]['content'] = save_content
        # Update the values
        content[module]['content'] = new_information
        # Check and insert questions
        module_content = ChapterQuestionGenerator(
                request.user,
                spec.spec_subject,
                module,
                content[module]['content'].copy()
            )
        content[module]['content'] = module_content
        spec.spec_content = content
        spec.save()
        return JsonResponse({'error': 0, 'message': 'Saved'})
    return JsonResponse({'error': 1, 'message': 'Error'})


def _undeletetopic(request):
    if request.method == 'POST':
        spec_id = request.POST['spec_id']
        module = request.POST['module']
        chapter = request.POST['chapter']
        topic = request.POST['topic']
        # Get objects
        spec = Specification.objects.get(
                user=request.user,
                pk=int(spec_id)
            )
        points = Point.objects.filter(
                user=request.user,
                p_level=spec.spec_level,
                p_subject=spec.spec_subject,
                p_moduel__iexact=module,
                p_chapter__iexact=chapter,
                p_topic__iexact=topic,
            )
        points.update(deleted=False)
        content = spec.spec_content.copy()
        if topic in content[module]['content'][chapter]['content'].keys():
            save_content = content[module]['content'][chapter]['content'][topic]['content']
        else:
            save_content = {}
        # Update the values
        ordered_topics = list(order_live_spec_content(content)[module]['content'][chapter]['content'].keys())
        ordered_topics = [topic] + ordered_topics
        new_information = insert_new_spec_order(ordered_topics, content[module]['content'][chapter]['content'], 'topic')
        new_information[topic]['content'] = save_content
        # Update the values
        content[module]['content'][chapter]['content'] = new_information
        spec.spec_content = content
        spec.save()
        return JsonResponse({'error': 0, 'message': 'Saved'})
    return JsonResponse({'error': 1, 'message': 'Error'})


def _undeletepoint(request):
    if request.method == 'POST':
        spec_id = request.POST['spec_id']
        module = request.POST['module']
        chapter = request.POST['chapter']
        topic = request.POST['topic']
        point = request.POST['point']
        # Get objects
        spec = Specification.objects.get(
                user=request.user,
                pk=int(spec_id)
            )
        points = Point.objects.filter(
                user=request.user,
                p_unique_id=point,
            )
        points.update(deleted=False)
        content = spec.spec_content.copy()
        # Update the values
        ordered_point = list(order_live_spec_content(content)[module]['content'][chapter]['content'][topic]['content'].keys())
        ordered_point = [point] + ordered_point
        new_information = insert_new_spec_order(ordered_point, content[module]['content'][chapter]['content'][topic]['content'], 'point')
        # Update the values
        content[module]['content'][chapter]['content'][topic]['content'] = new_information
        spec.spec_content = content
        spec.save()
        return JsonResponse({'error': 0, 'message': 'Saved'})
    return JsonResponse({'error': 1, 'message': 'Error'})


def _deletecourse(request):
    if request.method == 'POST':
        course_id = request.POST['Course_id']
        courses = Course.objects.filter(
                user=request.user,
                pk=course_id
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


def _deletemoduel(request):
    if request.method == 'POST':
        level = request.POST['level']
        subject = request.POST['subject']
        board = request.POST['board']
        name = request.POST['name']
        deleted_moduel = request.POST['delete_moduel']
        points = Point.objects.filter(
                user=request.user,
                p_level=level,
                p_subject=subject,
                p_moduel__iexact=deleted_moduel,
            )
        spec = Specification.objects.get(
                user=request.user,
                spec_level=level,
                spec_subject=subject,
                spec_board=board,
                spec_name=name,
            )
        if len(points) > 0:
            points.update(deleted=True)
            content = spec.spec_content
            if deleted_moduel in content.keys():
                content[deleted_moduel]['active'] = False
                content[deleted_moduel]['position'] = -1
                spec.spec_content = content
                spec.save()
            #
            messages.add_message(
                    request,
                    messages.INFO,
                    f'Module {deleted_moduel} was binned but not permanently deleted.',
                    extra_tags='alert-warning specmoduel'
                )
        else:
            messages.add_message(
                    request,
                    messages.INFO,
                    'Something is wrong, please check that the input is correct.',
                    extra_tags='alert-warning specmoduel'
                )
        kwargs = {
            'level': level,
            'subject': subject,
            'board': board,
            'name': name
        }
        return redirect(
                'dashboard:specmoduel',
                **kwargs
            )


def _deletechapter(request):
    if request.method == 'POST':
        level = request.POST['level']
        subject = request.POST['subject']
        module = request.POST['moduel']
        board = request.POST['board']
        name = request.POST['name']
        deleted_chapter = request.POST['delete_chapter']
        #
        points = Point.objects.filter(
                user=request.user,
                p_level=level,
                p_subject=subject,
                p_moduel=module,
                p_chapter=deleted_chapter,
            )
        spec = Specification.objects.get(
                user=request.user,
                spec_level=level,
                spec_subject=subject,
                spec_board=board,
                spec_name=name,
            )
        if len(points) > 0:
            points.update(deleted=True)
            content = spec.spec_content
            if module in content.keys():
                if deleted_chapter in content[module]['content'].keys():
                    content[module]['content'][deleted_chapter]['active'] = False
                    content[module]['content'][deleted_chapter]['position'] = -1
                    spec.spec_content = content
                    spec.save()
            #
            messages.add_message(
                    request,
                    messages.INFO,
                    f'chapter {deleted_chapter} was binned but not permanently deleted.',
                    extra_tags='alert-warning specmoduel'
                )
        else:
            messages.add_message(
                    request,
                    messages.INFO,
                    'Something is wrong, please check that the input is correct.',
                    extra_tags='alert-warning specmoduel'
                )
        kwargs = {
            'level': level,
            'subject': subject,
            'board': board,
            'name': name
        }
        return redirect(
                'dashboard:specmoduel',
                **kwargs
            )


def _deletetopic(request):
    if request.method == 'POST':
        level = request.POST['level']
        subject = request.POST['subject']
        module = request.POST['moduel']
        chapter = request.POST['chapter']
        board = request.POST['board']
        name = request.POST['name']
        deleted_topic = request.POST['delete_topic']
        #
        points = Point.objects.filter(
                user=request.user,
                p_level=level,
                p_subject=subject,
                p_moduel=module,
                p_chapter=chapter,
                p_topic__iexact=deleted_topic,
            )
        spec = Specification.objects.get(
                user=request.user,
                spec_level=level,
                spec_subject=subject,
                spec_board=board,
                spec_name=name,
            )
        if len(points) > 0:
            points.update(deleted=True)
            content = spec.spec_content
            content = spec.spec_content
            if module in content.keys():
                if chapter in content[module]['content'].keys():
                    if deleted_topic in content[module]['content'][chapter]['content'].keys():
                        content[module]['content'][chapter]['content'][deleted_topic]['active'] = False
                        content[module]['content'][chapter]['content'][deleted_topic]['position'] = -1
                        spec.spec_content = content
                        spec.save()
            #
            messages.add_message(
                    request,
                    messages.INFO,
                    f'Topic {deleted_topic} was binned but not permanently deleted.',
                    extra_tags='alert-warning spectopic'
                )
        else:
            messages.add_message(
                    request,
                    messages.INFO,
                    'Something is wrong, please check that the input is correct.',
                    extra_tags='alert-warning spectopic'
                )
        kwargs = {
            'level': level,
            'subject': subject,
            'module': module,
            'chapter': chapter,
            'board': board,
            'name': name
        }
        return redirect(
                'dashboard:spectopic',
                **kwargs
            )


def _deletepoint(request):
    if request.method == 'POST':
        level = request.POST['level']
        subject = request.POST['subject']
        module = request.POST['moduel']
        chapter = request.POST['chapter']
        topic = request.POST['topic']
        board = request.POST['board']
        name = request.POST['name']
        deleted_point = request.POST['delete_point']
        #
        points = Point.objects.filter(
                user=request.user,
                p_level=level,
                p_subject=subject,
                p_moduel=module,
                p_chapter=chapter,
                p_topic=topic,
                p_unique_id=deleted_point,
            )
        spec = Specification.objects.get(
                user=request.user,
                spec_level=level,
                spec_subject=subject,
                spec_board=board,
                spec_name=name,
            )
        if len(points) > 0:
            points.update(deleted=True)
            content = spec.spec_content
            if module in content.keys():
                    if chapter in content[module]['content'].keys():
                        if topic in content[module]['content'][chapter]['content'].keys():
                            if deleted_point in content[module]['content'][chapter]['content'][topic]['content'].keys():
                                content[module]['content'][chapter]['content'][topic]['content'][deleted_point]['active'] = False
                                content[module]['content'][chapter]['content'][topic]['content'][deleted_point]['position'] = -1
                                spec.spec_content = content
                                spec.save()
            #
            messages.add_message(
                    request,
                    messages.INFO,
                    f'Point {deleted_point} was binned but not permanently deleted.',
                    extra_tags='alert-warning spectopic'
                )
        else:
            messages.add_message(
                    request,
                    messages.INFO,
                    'Something is wrong, please check that the input is correct.',
                    extra_tags='alert-warning spectopic'
                )
        kwargs = {
            'level': level,
            'subject': subject,
            'board': board,
            'module': module,
            'chapter': chapter,
            'board': board,
            'name': name
        }
        return redirect(
                'dashboard:spectopic',
                **kwargs
            )


def _erasemodule(request):
    if request.method == 'POST':
        spec_id = request.POST['spec_id']
        deleted_moduel = request.POST['module']
        spec = Specification.objects.get(
                user=request.user,
                pk=spec_id
            )
        points = Point.objects.filter(
                user=request.user,
                p_level=spec.spec_level,
                p_subject=spec.spec_subject,
                p_moduel=deleted_moduel,
            )
        if len(points) > 0:
            points.update(deleted=True, erased=True)
            content = spec.spec_content
            if deleted_moduel in content.keys():
                content[deleted_moduel]['active'] = False
                content[deleted_moduel]['position'] = -1
                spec.spec_content = content
                spec.save()
            #
            return JsonResponse({'error': 0, 'message': 'Saved'})
    return JsonResponse({'error': 1, 'message': 'Error'})


def _erasechapter(request):
    if request.method == 'POST':
        spec_id = request.POST['spec_id']
        deleted_moduel = request.POST['module']
        deleted_chapter = request.POST['chapter']
        spec = Specification.objects.get(
                user=request.user,
                pk=spec_id
            )
        points = Point.objects.filter(
                user=request.user,
                p_level=spec.spec_level,
                p_subject=spec.spec_subject,
                p_moduel=deleted_moduel,
                p_chapter=deleted_chapter,
            )
        if len(points) > 0:
            points.update(deleted=True, erased=True)
            content = spec.spec_content
            if deleted_moduel in content.keys():
                content[deleted_moduel]['content'][deleted_chapter]['active'] = False
                content[deleted_moduel]['content'][deleted_chapter]['position'] = -1
                spec.spec_content = content
                spec.save()
            #
            return JsonResponse({'error': 0, 'message': 'Saved'})
    return JsonResponse({'error': 1, 'message': 'Error'})


def _erasetopic(request):
    if request.method == 'POST':
        spec_id = request.POST['spec_id']
        deleted_moduel = request.POST['module']
        deleted_chapter = request.POST['chapter']
        deleted_topic = request.POST['topic']
        spec = Specification.objects.get(
                user=request.user,
                pk=spec_id
            )
        points = Point.objects.filter(
                user=request.user,
                p_level=spec.spec_level,
                p_subject=spec.spec_subject,
                p_moduel=deleted_moduel,
                p_chapter=deleted_chapter,
                p_topic=deleted_topic,
            )
        if len(points) > 0:
            points.update(deleted=True, erased=True)
            content = spec.spec_content
            if deleted_moduel in content.keys():
                content[deleted_moduel]['content'][deleted_chapter]['content'][deleted_topic]['active'] = False
                content[deleted_moduel]['content'][deleted_chapter]['content'][deleted_topic]['position'] = -1
                spec.spec_content = content
                spec.save()
            #
            return JsonResponse({'error': 0, 'message': 'Saved'})
    return JsonResponse({'error': 1, 'message': 'Error'})


def _erasepoint(request):
    if request.method == 'POST':
        spec_id = request.POST['spec_id']
        deleted_moduel = request.POST['module']
        deleted_chapter = request.POST['chapter']
        deleted_topic = request.POST['topic']
        deleted_point = request.POST['point']
        spec = Specification.objects.get(
                user=request.user,
                pk=spec_id
            )
        points = Point.objects.filter(
                user=request.user,
                p_unique_id=deleted_point,
            )
        if len(points) > 0:
            points.update(deleted=True, erased=True)
            content = spec.spec_content
            if deleted_moduel in content.keys():
                content[deleted_moduel]['content'][deleted_chapter]['content'][deleted_topic]['content'][deleted_point]['active'] = False
                content[deleted_moduel]['content'][deleted_chapter]['content'][deleted_topic]['content'][deleted_point]['position'] = -1
                spec.spec_content = content
                spec.save()
            #
            return JsonResponse({'error': 0, 'message': 'Saved'})
    return JsonResponse({'error': 1, 'message': 'Error'})


def _savepointedit(request):
    if request.method == 'POST':
        point_id = request.POST['point_id']
        point = Point.objects.filter(user=request.user, pk=point_id)
        if len(point) == 1:
            form = MDEditorModleForm(request.POST, instance=point[0])
            if form.is_valid():
                form.save()
                content = form.cleaned_data['p_MDcontent']
                description_text = content.split('\n')
                description_content = {}
                for idd, v in enumerate(description_text):
                    description_content[idd] = {}
                    if '!(' in v:
                        left_over_text = v.split('!(')[0]
                        first_list = v.split('(')[1].split(')')
                        second_list = first_list[1].split('[')[1].split(']')
                        description_content[idd]['img'] = {}
                        description_content[idd]['img']['img_info'] = first_list[0]
                        description_content[idd]['img']['img_name'] = second_list[0]
                        left_over_text_after = second_list[1]
                    else:
                        description_content[idd]['text'] = v
                #
                point[0].p_content = description_content
                point[0].save()
                return JsonResponse({'error': 0, 'message': 'Saved'})
            return JsonResponse({'error': 1, 'message': 'Error'})
        return JsonResponse({'error': 1, 'message': 'Error'})
    return JsonResponse({'error': 1, 'message': 'Error'})


def _savequestionedit(request):
    if request.method == 'POST':
        question_id = request.POST['question_id']
        question = Question.objects.filter(user=request.user, pk=question_id)
        if len(question) == 1:
            form = MDEditorQuestionModleForm(request.POST, instance=question[0])
            if form.is_valid():
                form.save()
                content = form.cleaned_data['q_MDcontent']
                description_text = content.split('\n')
                description_content = {}
                for idd, v in enumerate(description_text):
                    description_content[idd] = {}
                    if '!(' in v:
                        first_list = v.split('(')[1].split(')')
                        second_list = first_list[1].split('[')[1].split(']')
                        description_content[idd]['img'] = {}
                        description_content[idd]['img']['img_info'] = first_list[0]
                        description_content[idd]['img']['img_name'] = second_list[0]
                    else:
                        description_content[idd]['text'] = v
                #
                question[0].q_content = description_content
                question[0].save()
                return JsonResponse({'error': 0, 'message': 'Saved'})
            return JsonResponse({'error': 1, 'message': 'Error'})
        return JsonResponse({'error': 1, 'message': 'Error'})
    return JsonResponse({'error': 1, 'message': 'Error'})


def _saveansweredit(request):
    if request.method == 'POST':
        question_id = request.POST['question_id']
        question = Question.objects.filter(user=request.user, pk=question_id)
        if len(question) == 1:
            form = MDEditorAnswerModleForm(request.POST, instance=question[0])
            if form.is_valid():
                form.save()
                content = form.cleaned_data['q_MDcontent_ans']
                description_text = content.split('\n')
                description_content = {}
                for idd, v in enumerate(description_text):
                    description_content[idd] = {}
                    if '!(' in v:
                        first_list = v.split('(')[1].split(')')
                        second_list = first_list[1].split('[')[1].split(']')
                        description_content[idd]['img'] = {}
                        description_content[idd]['img']['img_info'] = first_list[0]
                        description_content[idd]['img']['img_name'] = second_list[0]
                    else:
                        description_content[idd]['text'] = v
                #
                question[0].q_answer = description_content
                question[0].save()
                return JsonResponse({'error': 0, 'message': 'Saved'})
            return JsonResponse({'error': 1, 'message': 'Error'})
        return JsonResponse({'error': 1, 'message': 'Error'})
    return JsonResponse({'error': 1, 'message': 'Error'})

def _subjective_mark_question(request):
    if request.method == 'POST':
        course_id = request.POST['course_id']
        question_id = request.POST['question_id']
        precieved_difficulty = request.POST['precieved_difficulty']
        course = Course.objects.get(pk=course_id)
        question = Question.objects.get(user=request.user, pk=question_id)
        questiontrack, created = QuestionTrack.objects.get_or_create(
                    user=request.user,
                    course=course,
                    question=question
                )
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


def _mark_question(request):
    if request.method == 'POST':
        course_id = request.POST['course_id']
        question_id = request.POST['question_id']
        n_marks = request.POST['n_marks']
        course = Course.objects.get(pk=course_id)
        question = Question.objects.get(user=request.user, pk=question_id)
        questiontrack, created = QuestionTrack.objects.get_or_create(
                user=request.user,
                course=course,
                question=question
            )
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

def _mark_paper_question(request):
    if request.method == 'POST':
        #
        course_id = request.POST['course_id']
        paper_id = request.POST['paper_id']
        question_id = request.POST['question_id']
        n_marks = request.POST['n_marks']
        #
        course = Course.objects.get(pk=course_id)
        paper = UserPaper.objects.get(pk=paper_id)
        question = Question.objects.get(user=request.user, pk=question_id)
        questiontrack, created = QuestionTrack.objects.get_or_create(
                user=request.user,
                course=course,
                question=question
            )
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

def _show_answer(request):
    if request.method == 'POST':
        course_id = request.POST['course_id']
        question_id = request.POST['question_id']
        course = Course.objects.get(pk=course_id)
        question = Question.objects.get(user=request.user, pk=question_id)
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


