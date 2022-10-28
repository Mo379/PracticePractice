import os
import json
import requests
import collections
import pandas as pd
from collections import OrderedDict
from django.http import HttpResponseRedirect, FileResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.utils.functional import cached_property
from django.contrib import messages
from django.views import generic
from content.models import Video
from content.util.ContentSync import (
        QuestionSync,
        PointSync,
        VideoSync,
        SpecificationSync
        )
from content.util.ContentCRUD import (
        insert_new_spec_order,
        order_full_spec_content,
        QuestionCRUD,
        PointCRUD,
        SpecificationCRUD
    )
from view_breadcrumbs import BaseBreadcrumbMixin
from django.forms import model_to_dict
from content.models import *
from content.forms import MDEditorModleForm
from decouple import config as decouple_config
# Create your views here.


class ContentView(BaseBreadcrumbMixin, generic.ListView):
    template_name = 'content/content.html'
    context_object_name = 'context'

    @cached_property
    def crumbs(self):
        return [
                ("content", reverse("content:content"))
                ]

    def get_queryset(self):
        """Return all of the required hub information"""
        return 'content_content'


class QuestionsView(BaseBreadcrumbMixin, generic.ListView):
    template_name = 'content/questions.html'
    context_object_name = 'context'

    @cached_property
    def crumbs(self):
        return [
                ("content", reverse("content:content")),
                ("questions", reverse("content:questions"))
                ]

    def get_queryset(self):
        context = {}
        subjects = Question.objects.values(
                    'q_level',
                    'q_subject',
                ).distinct().order_by(
                    'q_level',
                    'q_subject',
                )
        subjects = [obj for obj in subjects]
        spec_subscriptions = SpecificationSubscription.objects.filter(
                user=self.request.user
            ) if self.request.user.is_authenticated else ''
        #
        Note_objs = []
        spec_names = {}
        for subject in subjects:
            # optain the subscribed spec or the unviersal spec
            subject_loc = subject['q_level']+subject['q_subject']
            status = 0
            for user_spec in spec_subscriptions:
                spec = user_spec.specification
                spec_loc = spec.spec_level+spec.spec_subject
                if spec_loc == subject_loc:
                    content = spec.spec_content
                    status = 1
                    break
            if status == 0:
                spec = Specification.objects.get(
                        spec_level=subject['q_level'],
                        spec_subject=subject['q_subject'],
                        spec_board='Universal',
                        spec_name='Universal',
                    )
                content = spec.spec_content
            content = order_full_spec_content(content)
            #
            for key, value in content.items():
                if value['active'] == True:
                    for k, v in value['content'].items():
                        if v['active'] == True:
                                Note_objs.append({
                                        'p_level': subject['q_level'],
                                        'p_subject': subject['q_subject'],
                                        'p_moduel': key,
                                        'p_chapter': k,
                                    })
                                spec_names[subject['q_subject']] = [spec.spec_board,spec.spec_name]
        df = pd.DataFrame(Note_objs)
        dic = OrderedDict()
        for le, s, m, c in zip(
                list(df['p_level']),
                list(df['p_subject']),
                list(df['p_moduel']),
                list(df['p_chapter']),
                ):
            if le not in dic:
                dic[le] = OrderedDict()
            if s not in dic[le]:
                dic[le][s] = OrderedDict()
            if m not in dic[le][s]:
                dic[le][s][m] = []
            dic[le][s][m].append(c)
        context['spec'] = spec
        context['spec_names'] = spec_names
        context['questions'] = dic
        return context


class QuestionView(BaseBreadcrumbMixin, generic.ListView):
    template_name = 'content/question.html'
    context_object_name = 'context'

    @cached_property
    def crumbs(self):
        return [
                ("content", reverse("content:content")),
                ("questions", reverse("content:questions")),
                ("question", '')
                ]

    def get_queryset(self):
        context = {}
        level = self.kwargs['level']
        subject = self.kwargs['subject']
        board = self.kwargs['board']
        specification = self.kwargs['specification']
        module = self.kwargs['module']
        chapter = self.kwargs['chapter']
        context['title'] = chapter
        #
        spec = Specification.objects.get(
                spec_level=level,
                spec_subject=subject,
                spec_board=board,
                spec_name=specification
            )
        chapter_qs = spec.spec_content[module]['content'][chapter]['questions']
        dic = OrderedDict()
        question = None
        for difficulty in range(5):
            difficulty += 1
            d = str(difficulty)
            if len(chapter_qs[d]) >0:
                for question in chapter_qs[d]:
                    if d not in dic:
                        dic[d] = []
                    dic[d].append(Question.objects.get(q_unique_id=question))
        context['sampl_object'] = Question.objects.get(q_unique_id=question) if question else None
        context['questions'] = dic if question else None
        return context


class NotesView(BaseBreadcrumbMixin, generic.ListView):
    template_name = 'content/notes.html'
    context_object_name = 'context'

    @cached_property
    def crumbs(self):
        return [
                ("content", reverse("content:content")),
                ("notes", reverse("content:notes")),
                ]

    def get_queryset(self):
        """Return all of the required hub information"""
        context = {}
        subjects = Point.objects.values(
                    'p_level',
                    'p_subject',
                ).distinct().order_by(
                    'p_level',
                    'p_subject',
                )
        subjects = [obj for obj in subjects]
        spec_subscriptions = SpecificationSubscription.objects.filter(
                user=self.request.user
            ) if self.request.user.is_authenticated else ''
        #
        Note_objs = []
        spec_names = {}
        for subject in subjects:
            # optain the subscribed spec or the unviersal spec
            subject_loc = subject['p_level']+subject['p_subject']
            status = 0
            for user_spec in spec_subscriptions:
                spec = user_spec.specification
                spec_loc = spec.spec_level+spec.spec_subject
                if spec_loc == subject_loc:
                    content = spec.spec_content
                    status = 1
                    break
            if status == 0:
                spec = Specification.objects.get(
                        spec_level=subject['p_level'],
                        spec_subject=subject['p_subject'],
                        spec_board='Universal',
                        spec_name='Universal',
                    )
                content = spec.spec_content
            content = order_full_spec_content(content)
            #
            for key, value in content.items():
                if value['active'] == True:
                    for k, v in value['content'].items():
                        if v['active'] == True:
                            Note_objs.append({
                                    'p_level': subject['p_level'],
                                    'p_subject': subject['p_subject'],
                                    'p_moduel': key,
                                    'p_chapter': k,
                                })
                            spec_names[subject['p_subject']] = [spec.spec_board,spec.spec_name]
        df = pd.DataFrame(Note_objs)
        dic = OrderedDict()
        for le, s, m, c in zip(
                list(df['p_level']),
                list(df['p_subject']),
                list(df['p_moduel']),
                list(df['p_chapter']),
                ):
            if le not in dic:
                dic[le] = OrderedDict()
            if s not in dic[le]:
                dic[le][s] = OrderedDict()
            if m not in dic[le][s]:
                dic[le][s][m] = []
            dic[le][s][m].append(c)
        context['notes'] = dic
        context['spec_names'] = spec_names
        return context



class NoteArticleView(BaseBreadcrumbMixin, generic.ListView):
    template_name = 'content/note.html'
    context_object_name = 'context'

    @cached_property
    def crumbs(self):
        return [
                ("content", reverse("content:content")),
                ("notes", reverse("content:notes")),
                ("article", ''),
                ]

    def get_queryset(self):
        """Return all of the required hub information"""
        context = {}
        # Get details of page
        level = self.kwargs['level']
        subject = self.kwargs['subject']
        board = self.kwargs['board']
        spec_name = self.kwargs['specification']
        module = self.kwargs['module']
        chapter = self.kwargs['chapter']
        context['title'] = chapter
        #
        spec = Specification.objects.get(
                    spec_level=level,
                    spec_subject=subject,
                    spec_board=board,
                    spec_name=spec_name
                )
        content = spec.spec_content
        content = order_full_spec_content(content)
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
        context['spec'] = spec
        context['next'] = next_link
        context['previous'] = previous_link
        editor_form = MDEditorModleForm()
        context['editor_form'] = editor_form
        return context


class PapersView(BaseBreadcrumbMixin, generic.ListView):
    template_name = 'content/papers.html'
    context_object_name = 'context'

    @cached_property
    def crumbs(self):
        return [
                ("content", reverse("content:content")),
                ("papers", reverse("content:papers")),
                ]

    def get_queryset(self):
        context = {}
        Notes = Question.objects.values(
                    'q_subject',
                    'q_board',
                    'q_board_moduel',
                    'q_exam_year',
                    'q_exam_month',
                    'q_is_exam',
                ).distinct().order_by(
                    'q_subject',
                    'q_board',
                    'q_board_moduel',
                    'q_exam_year',
                    'q_exam_month',
                ).filter(q_is_exam=1)
        Notes_objs = [obj for obj in Notes]
        df = pd.DataFrame(Notes_objs)
        dic = {}
        for su, b, mod, y, mon in zip(
                list(df['q_subject']),
                list(df['q_board']),
                list(df['q_board_moduel']),
                list(df['q_exam_year']),
                list(df['q_exam_month']),
                ):
            if su not in dic:
                dic[su] = {}
            if b not in dic[su]:
                dic[su][b] = {}
            if mod not in dic[su][b]:
                dic[su][b][mod] = {}
            if y not in dic[su][b][mod]:
                dic[su][b][mod][y] = {}
            if mon not in dic[su][b][mod][y]:
                dic[su][b][mod][y][mon] = []
            dic[su][b][mod][y][mon].append('Paper')
        context['papers'] = dic
        return context




class PaperView(BaseBreadcrumbMixin, generic.ListView):
    template_name = 'content/paper.html'
    context_object_name = 'context'

    @cached_property
    def crumbs(self):
        return [
                ("content", reverse("content:content")),
                ("papers", reverse("content:papers")),
                ("paper", ''),
                ]

    def get_queryset(self):
        context = {}
        subject = self.kwargs['subject']
        board = self.kwargs['board']
        board_module = self.kwargs['board_moduel']
        exam_year = self.kwargs['exam_year']
        exam_month = self.kwargs['exam_month']
        context['title'] = 'paper title'
        article_objects = Question.objects.filter(
                    q_subject=subject,
                    q_board=board,
                    q_board_moduel=board_module,
                    q_exam_year=exam_year,
                    q_exam_month=exam_month,
                ).order_by('q_exam_num')
        article_questions = [model_to_dict(obj) for obj in article_objects]
        df = pd.DataFrame(article_questions)
        dic = OrderedDict()
        for exam_num, p_id in zip(list(df['q_exam_num']), list(df['id'])):
            if exam_num not in dic:
                dic[exam_num] = []
            dic[exam_num].append(Question.objects.get(pk=p_id))
        context['sampl_object'] = Question.objects.get(pk=p_id)
        context['questions'] = dic
        return context


def _media(request):
    path = request.GET.get('path', None)
    content_dir = decouple_config('content_dir')
    file_loc = os.path.join(content_dir, path)
    try:
        fsock = open(file_loc, "rb")
    except Exception as e:
        return None
    else:
        return FileResponse(fsock)


def _syncnotes(request):
    try:
        sync_obj = PointSync()
        sync_obj.sync()
    except Exception as e:
        messages.add_message(
                request,
                messages.INFO,
                'Failed to sync notes.'+str(e),
                extra_tags='alert-danger syncnotes_form'
            )
    else:
        messages.add_message(
                request,
                messages.INFO,
                'Successfully synced notes',
                extra_tags='alert-success syncnotes_form'
            )
    return redirect('dashboard:superuser_contentmanagement')


def _syncquestions(request):
    try:
        sync_obj = QuestionSync()
        sync_obj.sync()
    except Exception as e:
        messages.add_message(
                request,
                messages.INFO,
                'Failed to sync questions.'+str(e),
                extra_tags='alert-danger syncquestions_form'
            )
    else:
        messages.add_message(
                request,
                messages.INFO,
                'Successfully synced questions',
                extra_tags='alert-success syncquestions_form'
            )
    return redirect('dashboard:superuser_contentmanagement')


def _syncspecifications(request):
    try:
        sync_obj = SpecificationSync()
        sync_obj.sync()
    except Exception as e:
        messages.add_message(
                request,
                messages.INFO,
                'Failed to sync specifications.'+str(e),
                extra_tags='alert-danger syncspecifications_form'
            )
    else:
        messages.add_message(
                request,
                messages.INFO,
                'Successfully synced specifications',
                extra_tags='alert-success syncspecifications_form'
            )
    return redirect('dashboard:superuser_contentmanagement')


def _syncspecquestions(request):
    specs = Specification.objects.all()
    for spec in specs:
        for m_name, moduel in spec.spec_content.items():
            for c_name, chapter in moduel['content'].items():
                questions = chapter['questions']
                keys = questions.keys()
                for i in range(5):
                    i = i+1
                    if i not in keys:
                        questions[i] = []
                    n_questions = len(questions[i])
                    if n_questions < 5:
                        n_diff = 5 - n_questions
                        new_questions = Question.objects.filter(
                                q_level=spec.spec_level,
                                q_subject=spec.spec_subject,
                                q_moduel=m_name,
                                q_chapter=c_name,
                                q_difficulty=i
                            ).exclude(
                                    q_unique_id__in=questions[i]
                                )[:n_diff]
                        for new_q in new_questions:
                            questions[i].append(new_q.q_unique_id)
                    else:
                        questions[i] = questions[i][0:5]
                chapter['questions'] = questions
        spec.save()
        json_content = json.dumps(spec.spec_content, indent=4)
        crud_obj = SpecificationCRUD()
        crud_obj.Update(
                spec.spec_level,
                spec.spec_subject,
                spec.spec_board,
                spec.spec_name,
                json_content
            )
    messages.add_message(
            request,
            messages.INFO,
            'Successfully synced specification questions',
            extra_tags='alert-success syncspecquestions_form'
        )
    return redirect('dashboard:superuser_contentmanagement')


def _syncvideos(request):
    try:
        sync_obj = VideoSync()
        sync_obj.sync()
    except Exception as e:
        messages.add_message(
                request,
                messages.INFO,
                'Failed to sync Videos.'+str(e),
                extra_tags='alert-danger syncvideos_form'
            )
    else:
        messages.add_message(
                request,
                messages.INFO,
                'Successfully synced videos',
                extra_tags='alert-success syncvideos_form'
            )
    return redirect('dashboard:superuser_contentmanagement')


def _checkvideohealth(request):
    try:
        videos = Video.objects.all()
        for video in videos:
            video_url = video.v_link
            print(video_url)
            if 'embed' in video_url or 'watch?v=' in video_url:
                video_url = video_url.replace('embed/', 'watch?v=')
                r = requests.get(video_url)
                if "Video unavailable" in r.text:
                    video.v_health = False
                else:
                    video.v_health = True
            else:
                video.v_health = False
            video.save()
    except Exception as e:
        messages.add_message(
                request,
                messages.INFO,
                'Failed to check video health.'+str(e),
                extra_tags='alert-danger videohealth_form'
            )
    else:
        messages.add_message(
                request,
                messages.INFO,
                'Successfully checked all videos',
                extra_tags='alert-success videohealth_form'
            )
    return redirect('dashboard:superuser_contentmanagement')


def _inheritfromspec(request):
    if request.method == 'POST':
        level = request.POST['level']
        subject = request.POST['subject']
        board = request.POST['board']
        name = request.POST['name']
        inheritance_parent = request.POST['inheritance_parent'].split(' ')
        # Get objects
        child_spec = Specification.objects.get(
                spec_level=level,
                spec_subject=subject,
                spec_board=board,
                spec_name=name
            )
        parent_spec = Specification.objects.filter(
                spec_level=level,
                spec_subject=subject,
                spec_board=inheritance_parent[0],
                spec_name=inheritance_parent[1],
            )
        if parent_spec:
            parent_spec = Specification.objects.get(
                    spec_level=level,
                    spec_subject=subject,
                    spec_board=inheritance_parent[0],
                    spec_name=inheritance_parent[1],
                )
            content = parent_spec.spec_content
            child_spec.spec_content = content
            child_spec.save()
            # Update the values
            messages.add_message(
                    request,
                    messages.INFO,
                    'Successful Inheritance',
                    extra_tags='alert-success specmoduel'
                )
        else:
            messages.add_message(
                    request,
                    messages.INFO,
                    'Something went wront, check that the parent input is correct.',
                    extra_tags='alert-danger specmoduel'
                )
        #
        kwargs = {
            'level': level,
            'subject': subject,
            'board': board,
            'name': name,
        }
        return redirect(
                'dashboard:superuser_specmoduel',
                **kwargs
            )


def _ordermoduels(request):
    if request.method == 'POST':
        level = request.POST['level']
        subject = request.POST['subject']
        board = request.POST['board']
        name = request.POST['name']
        ordered_moduels = request.POST.getlist('ordered_items[]')
        if 'completed' in request.POST:
            completed = True
        else:
            completed = False
        # Get objects
        spec = Specification.objects.get(
                spec_level=level,
                spec_subject=subject,
                spec_board=board,
                spec_name=name
            )
        content = spec.spec_content.copy()
        new_information = insert_new_spec_order(ordered_moduels, content, 'moduel')
        content = new_information
        # Update the values
        if completed:
            spec.spec_health = True
        else:
            spec.spec_health = False
        spec.spec_content = content
        spec.save()
        json_content = json.dumps(spec.spec_content, indent=4)
        crud_obj = SpecificationCRUD()
        crud_obj.Update(level, subject, board, name, json_content)
        messages.add_message(
                request,
                messages.INFO,
                'Specification Moduels Updated!',
                extra_tags='alert-success specmoduel'
            )

        #
        kwargs = {
            'level': level,
            'subject': subject,
            'board': board,
            'name': name,
        }
        return redirect(
                'dashboard:superuser_specmoduel',
                **kwargs
            )


def _orderchapters(request):
    if request.method == 'POST':
        level = request.POST['level']
        subject = request.POST['subject']
        board = request.POST['board']
        name = request.POST['name']
        moduel = request.POST['moduel']
        ordered_chapters = request.POST.getlist('ordered_items[]')
        # Get objects
        spec = Specification.objects.get(
                spec_level=level,
                spec_subject=subject,
                spec_board=board,
                spec_name=name
            )
        content = spec.spec_content.copy()
        new_information = insert_new_spec_order(
                ordered_chapters,
                content[moduel]['content'],
                'chapter'
            )
        content[moduel]['content'] = new_information
        spec.spec_content = content
        spec.save()
        json_content = json.dumps(spec.spec_content, indent=4)
        crud_obj = SpecificationCRUD()
        crud_obj.Update(level, subject, board, name, json_content)
        messages.add_message(
                request,
                messages.INFO,
                'Specification Moduel-Chapters Updated !',
                extra_tags='alert-success specchapter'
            )
        #
        kwargs = {
            'level': level,
            'subject': subject,
            'board': board,
            'name': name,
            'module': moduel,
        }
        return redirect(
                'dashboard:superuser_specchapter',
                **kwargs
            )


def _ordertopics(request):
    if request.method == 'POST':
        level = request.POST['level']
        subject = request.POST['subject']
        board = request.POST['board']
        name = request.POST['name']
        moduel = request.POST['moduel']
        chapter = request.POST['chapter']
        ordered_topics = request.POST.getlist('ordered_items[]')
        # Get objects
        spec = Specification.objects.get(
                spec_level=level,
                spec_subject=subject,
                spec_board=board,
                spec_name=name
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
        json_content = json.dumps(spec.spec_content, indent=4)
        crud_obj = SpecificationCRUD()
        crud_obj.Update(level, subject, board, name, json_content)
        messages.add_message(
                request,
                messages.INFO,
                'Specification Chapter-Topics Updated !',
                extra_tags='alert-success spectopic'
            )
        #
        kwargs = {
            'level': level,
            'subject': subject,
            'board': board,
            'name': name,
            'module': moduel,
            'chapter': chapter,
        }
        return redirect(
                'dashboard:superuser_spectopic',
                **kwargs
            )

def _orderpoints(request):
    if request.method == 'POST':
        level = request.POST['level']
        subject = request.POST['subject']
        board = request.POST['board']
        name = request.POST['name']
        moduel = request.POST['moduel']
        chapter = request.POST['chapter']
        topic = request.POST['topic']
        ordered_topics = request.POST.getlist('ordered_items[]')
        # Get objects
        spec = Specification.objects.get(
                spec_level=level,
                spec_subject=subject,
                spec_board=board,
                spec_name=name
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
        json_content = json.dumps(spec.spec_content, indent=4)
        crud_obj = SpecificationCRUD()
        crud_obj.Update(level, subject, board, name, json_content)
        messages.add_message(
                request,
                messages.INFO,
                'Specification Topic-Points Updated !',
                extra_tags='alert-success specpoint'
            )
        #
        kwargs = {
            'level': level,
            'subject': subject,
            'board': board,
            'name': name,
            'module': moduel,
            'chapter': chapter,
            'topic': topic,
        }
        return redirect(
                'dashboard:superuser_specpoint',
                **kwargs
            )


def _specificationsubscription(request, level, subject, board, name):
    if request.method == 'GET':
        spec = Specification.objects.get(
                spec_level=level,
                spec_subject=subject,
                spec_board=board,
                spec_name=name
            )
        new_spec_region = level+subject
        #
        current_subscriptions = SpecificationSubscription.objects.filter(user=request.user)
        for cs in current_subscriptions:
            old_spec = cs.specification
            spec_region = old_spec.spec_level+old_spec.spec_subject
            if new_spec_region == spec_region:
                cs.delete()
        SpecificationSubscription.objects.create(user=request.user, specification=spec)
        #
        messages.add_message(
                request,
                messages.INFO,
                'Specification Subscriptions Updated!',
                extra_tags='alert-success specsubscriptions'
            )
        #
        return redirect(
                'dashboard:student_contentmanagement',
            )
