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
        Notes = Question.objects.values(
                    'q_level',
                    'q_subject',
                    'q_moduel',
                    'q_chapter',
                ).distinct().order_by(
                    'q_level',
                    'q_subject',
                    'q_moduel',
                    'q_chapter',
                )
        Notes_objs = [obj for obj in Notes]
        df = pd.DataFrame(Notes_objs)
        dic = {}
        for le, s, m, c in zip(
                list(df['q_level']),
                list(df['q_subject']),
                list(df['q_moduel']),
                list(df['q_chapter']),
                ):
            if le not in dic:
                dic[le] = {}
            if s not in dic[le]:
                dic[le][s] = {}
            if m not in dic[le][s]:
                dic[le][s][m] = []
            dic[le][s][m].append(c)
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
        specification = self.kwargs['specification']
        module = self.kwargs['module']
        chapter = self.kwargs['chapter']
        context['title'] = chapter
        article_objects = Question.objects.filter(
                    q_subject=subject,
                    q_moduel=module,
                    q_chapter=chapter,
                ).order_by('q_difficulty')
        article_questions = [model_to_dict(obj) for obj in article_objects]
        df = pd.DataFrame(article_questions)
        dic = OrderedDict()
        for difficulty, p_id in zip(list(df['q_difficulty']), list(df['id'])):
            if difficulty not in dic:
                dic[difficulty] = []
            dic[difficulty].append(Question.objects.get(pk=p_id))
        context['sampl_object'] = Question.objects.get(pk=p_id)
        context['questions'] = dic
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
        Notes = Point.objects.values(
                    'p_level',
                    'p_subject',
                    'p_moduel',
                    'p_chapter',
                ).distinct().order_by(
                    'p_level',
                    'p_subject',
                    'p_moduel',
                    'p_chapter',
                )
        Notes_objs = [obj for obj in Notes]
        print(Notes_objs)
        df = pd.DataFrame(Notes_objs)
        dic = {}
        for le, s, m, c in zip(
                list(df['p_level']),
                list(df['p_subject']),
                list(df['p_moduel']),
                list(df['p_chapter']),
                ):
            if le not in dic:
                dic[le] = {}
            if s not in dic[le]:
                dic[le][s] = {}
            if m not in dic[le][s]:
                dic[le][s][m] = []
            dic[le][s][m].append(c)
        context['notes'] = dic
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
        level = self.kwargs['level']
        subject = self.kwargs['subject']
        specification = self.kwargs['specification']
        module = self.kwargs['module']
        chapter = self.kwargs['chapter']
        context['title'] = chapter
        article_objects = Point.objects.filter(
                    p_subject=subject,
                    p_moduel=module,
                    p_chapter=chapter,
                ).order_by('p_chapter', 'p_topic', 'p_number')
        article_points = [model_to_dict(obj) for obj in article_objects]
        df = pd.DataFrame(article_points)
        dic = {}
        for topic, p_id in zip(list(df['p_topic']), list(df['id'])):
            if topic not in dic:
                dic[topic] = []
            dic[topic].append(Point.objects.get(pk=p_id))
        context['sampl_object'] = Point.objects.get(pk=p_id)
        context['article'] = dic
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
        print(new_information)
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

