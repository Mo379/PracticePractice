import os
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
        page = self.kwargs['page']
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
        context['article'] = dic
        editor_form = MDEditorModleForm()
        context['editor_form'] = editor_form
        return context


class PaperView(BaseBreadcrumbMixin, generic.ListView):
    template_name = 'content/paper.html'
    context_object_name = 'context'

    @cached_property
    def crumbs(self):
        return [
                ("content", reverse("content:content")),
                ("paper", reverse("content:paper")),
                ]

    def get_queryset(self):
        """Return all of the required hub information"""
        return 'content_paper'


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
