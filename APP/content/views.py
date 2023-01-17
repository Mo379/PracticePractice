import pandas as pd
import yaml
from django.conf import settings
import collections
from collections import OrderedDict
from django.shortcuts import redirect
from django.urls import reverse
from django.http import JsonResponse, HttpResponseRedirect
from django.utils.functional import cached_property
from django.contrib import messages
from django.views import generic
from content.util.GeneralUtil import (
        TagGenerator,
        insert_new_spec_order,
        order_full_spec_content,
        TranslatePointContent,
        TranslateQuestionContent,
    )
from view_breadcrumbs import BaseBreadcrumbMixin
from django.forms import model_to_dict
from content.models import *
from content.forms import MDEditorModleForm, MDEditorQuestionModleForm
from braces.views import (
        LoginRequiredMixin,
        GroupRequiredMixin,
        SuperuserRequiredMixin,
    )
from mdeditor.configs import MDConfig
from io import BytesIO
from PP2.utils import h_encode, h_decode
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
        course_subscriptions = CourseSubscription.objects.filter(
                user=self.request.user
            ).order_by('-subscription_created_at') if self.request.user.is_authenticated else False
        if course_subscriptions:
            context['courses'] = course_subscriptions
        else:
            context['courses'] = []
        #
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
        context['notes'] = dic
        context['spec_names'] = spec_names
        context['course'] = course
        return context



class NoteArticleView(
        LoginRequiredMixin,
        BaseBreadcrumbMixin,
        generic.ListView
        ):
    login_url = 'user:login'
    redirect_field_name = False
    template_name = 'content/note.html'
    context_object_name = 'context'

    @cached_property
    def crumbs(self):
        return [
                ("content", reverse("content:content")),
                ("notes", reverse("content:notes", kwargs={'course_id':self.kwargs['course_id']})),
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


class QuestionBankView(
        LoginRequiredMixin,
        BaseBreadcrumbMixin,
        generic.ListView
        ):
    login_url = 'user:login'
    redirect_field_name = False
    template_name = 'content/questionbank.html'
    context_object_name = 'context'

    @cached_property
    def crumbs(self):
        return [
                ("content", reverse("content:content")),
                ("question bank", '')
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
                ).order_by('-pap_creation_time')[:25]
        #
        content = order_full_spec_content(content)
        moduels = OrderedDict({i: moduel for i, moduel in enumerate(content)})
        chapters = collections.defaultdict(list)
        for m_key in moduels:
            chapter_list = [chapter for i, chapter in enumerate(content[moduels[m_key]]['content'])]
            chapters[moduels[m_key]] = chapter_list
        context['content'] = content
        context['moduels'] = moduels
        context['chapters'] = chapters
        context['course'] = course
        context['questionhistory'] = question_history
        context['paperhistory'] = paper_history
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
        content = order_full_spec_content(content)
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
        context['sampl_object'] = Question.objects.get(q_unique_id=question) if question else None
        context['questions'] = dic if question else None
        context['course'] = course
        context['module'] = module
        context['chapter'] = chapter
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
                ("custompaper", '')
            ]

    def get_queryset(self):
        context = {}
        paper_id = self.kwargs['paper_id']
        paper = UserPaper.objects.get(pk=paper_id)
        #
        context['paper'] = paper
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
        for topic, p_id in zip(list(df['p_topic']), list(df['id'])):
            if topic not in dic:
                dic[topic] = []
            dic[topic].append(Point.objects.get(pk=p_id))
        #
        context['sampl_object'] = Point.objects.get(pk=p_id)
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
        point.p_MDcontent = translated_content
        #
        editor_form = MDEditorModleForm(instance=point)
        context['spec'] = spec
        context['point'] = point
        context['editor_form'] = editor_form
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
        question.q_MDcontent = translated_content
        #
        editor_form = MDEditorQuestionModleForm(instance=question)
        context['spec'] = spec
        context['question'] = question
        context['editor_form'] = editor_form
        return context


def _inheritfromspec(request):
    if request.method == 'POST':
        level = request.POST['level']
        subject = request.POST['subject']
        board = request.POST['board']
        name = request.POST['name']
        parent_id = request.POST['parent_spec_id']
        child_id = request.POST['child_spec_id']
        # Get objects
        try:
            parent_spec = Specification.objects.get(
                    user=request.user,
                    pk=parent_id
                )
            child_spec = Specification.objects.get(
                    user=request.user,
                    pk=child_id
                )
            content = parent_spec.spec_content
            child_spec.spec_content = content
            child_spec.save()
            # Update the values
        except Exception:
            messages.add_message(
                    request,
                    messages.INFO,
                    'Something went wrong, check that the parent input is correct.',
                    extra_tags='alert-danger specmoduel'
                )
        else:
            messages.add_message(
                    request,
                    messages.INFO,
                    'Successful Inheritance',
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
                'dashboard:specmoduel',
                **kwargs
            )


def _add_collaborator(request):
    if request.method == 'POST':
        #
        email = request.POST['Collaborator_email']
        collaborator_type = request.POST['Collaborator_type']
        spec_id = h_decode(request.POST['spec_id'])
        #
        try:
            user_collaborator = User.objects.get(
                    email__iexact=email,
                    )
            spec = Specification.objects.get(pk=spec_id)
        except Exception as e:
            messages.add_message(
                    request,
                    messages.INFO,
                    'Something went wrong, check that the email and all other fields are correct and valid.' + str(e),
                    extra_tags='alert-danger specification'
                )
            return redirect(
                    'dashboard:specifications',
                )
        if user_collaborator == spec.user:
            messages.add_message(
                    request,
                    messages.INFO,
                    'The creator of the specification cannot become a collaborator.',
                    extra_tags='alert-danger specification'
                )
            return redirect(
                    'dashboard:specifications',
                )
        if collaborator_type in ['1', '2', '3']:
            history_check = Collaborator.objects.filter(
                    orchistrator=spec.user,
                    user=user_collaborator,
                    specification=spec,
                    deleted=False
                )
            if len(history_check) == 0:
                obj_collaborator = Collaborator(
                        orchistrator=spec.user,
                        user=user_collaborator,
                        specification=spec,
                        collaborator_type=int(collaborator_type)
                    )
                obj_collaborator.save()
                # mail
                to_email = user_collaborator.email
                mail_subject = 'Collaboration invite.'
                mail_sender = settings.EMAIL_MAIN
                message = str(
                    f"You have a new invitation from {spec.user.first_name} " +
                    f"{spec.user.last_name} to become a collaborator as a " +
                    f"{Collaborator.type_choices[int(collaborator_type)-1][1]} " +
                    f"for the following specification: \n ({str(spec)}) \n" +
                    "If you would like to accept this invitation see this page: \n" +
                    f"({settings.SITE_URL}/dashboard/specifications)"
                )
                _send_email(
                        mail_subject,
                        message,
                        mail_sender,
                        to_email,
                    )
                messages.add_message(
                        request,
                        messages.INFO,
                        'An invitation has been sent to your collaborator.',
                        extra_tags='alert-success specification'
                    )
            else:
                messages.add_message(
                        request,
                        messages.INFO,
                        'This collaborator already has a role for this specification.',
                        extra_tags='alert-warning specification'
                    )
            return redirect(
                    'dashboard:specifications',
                )
        return redirect(
                'dashboard:specifications',
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
                user=request.user,
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
            spec.spec_completion = True
        else:
            spec.spec_completion = False
        spec.spec_content = content
        spec.save()
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
                'dashboard:specmoduel',
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
                'dashboard:specchapter',
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
                'dashboard:spectopic',
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
                'dashboard:specpoint',
                **kwargs
            )


def _createcourse(request):
    if request.method == 'POST':
        course_name = request.POST['course_name']
        spec_id = request.POST['spec_id']
        version_name = request.POST['version_name']
        version_note = request.POST['version_note']
        specs = Specification.objects.filter(
                pk=spec_id
            )
        #
        if len(specs) == 1:
            try:
                new_course = Course.objects.create(
                            user=request.user,
                            course_name=course_name,
                            specification=specs[0]
                        )
                CourseVersion.objects.create(
                            course=new_course,
                            version_number=1,
                            version_name=version_name,
                            version_content=specs[0].spec_content,
                            version_note=version_note,
                        )
            except Exception:
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
        else:
            messages.add_message(
                    request,
                    messages.INFO,
                    'Input can only be alphanumeric!',
                    extra_tags='alert-warning course'
                )
        #
        return redirect(
                'dashboard:mycourses',
            )


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


def _updatecourseinformation(request):
    if request.method == 'POST':
        course_id = request.POST['course_id']
        course_name = request.POST['new_name']
        course_upload_image = request.FILES.get("course_thmbnail", None)
        course_question_bank_only = request.POST.get('question_bank_only')
        if course_question_bank_only == 'on':
           course_question_bank_only = True
        else:
           course_question_bank_only = False
        course_skills = request.POST.getlist('ordered_items_skills[]')
        course_objectives = request.POST.getlist('ordered_items_objectives[]')
        course_summary = request.POST['course_summary']
        course_level = request.POST['course_level']
        course_language = request.POST['course_language']
        course_estimated_time = request.POST['estimated_time']
        courses = Course.objects.filter(
                user=request.user,
                pk=course_id
            )
        #
        if len(courses) == 1:
            try:
                course = courses[0]
                course.course_name = course_name
                course.course_summary = course_summary
                course.course_level = course_level
                course.course_language = course_language
                course.course_estimated_time = course_estimated_time
                course.course_question_bank_only = course_question_bank_only
                #
                course.course_skills = {idd: skill for idd, skill in enumerate(course_skills)}
                course.course_learning_objectives = {idd: skill for idd, skill in enumerate(course_objectives)}
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
                        'Something went wrong could not create subscription.',
                        extra_tags='alert-warning marketcourse'
                    )
            else:
                messages.add_message(
                        request,
                        messages.INFO,
                        'You have subscribed to this course, goodluck with your studies!',
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
                'dashboard:marketcourse', course_id=course_id
            )


def _createspec(request):
    if request.method == 'POST':
        spec_level = request.POST['spec_level']
        spec_subject = request.POST['spec_subject']
        spec_board = request.POST['spec_board']
        spec_name = request.POST['spec_name']
        #
        if spec_level.isalnum() and spec_subject.isalnum() and \
                spec_board.isalnum() and spec_name.isalnum():
            try:
                specs = Specification.objects.filter(
                        user=request.user,
                        spec_level=spec_level,
                        spec_subject=spec_subject,
                        spec_board=spec_board,
                        spec_name=spec_name,
                    )
                if len(specs) == 0:
                    Specification.objects.create(
                            user=request.user,
                            spec_level=spec_level,
                            spec_subject=spec_subject,
                            spec_board=spec_board,
                            spec_name=spec_name,
                        )
                else:
                    spec = specs[0]
                    spec.deleted = False
                    spec.save()
            except Exception:
                messages.add_message(
                        request,
                        messages.INFO,
                        'Something went wrong could not create spec',
                        extra_tags='alert-warning specification'
                    )
            else:
                messages.add_message(
                        request,
                        messages.INFO,
                        'Specification Was Created',
                        extra_tags='alert-success specification'
                    )
        else:
            messages.add_message(
                    request,
                    messages.INFO,
                    'Input can only be alphanumeric!',
                    extra_tags='alert-warning specification'
                )
        #
        return redirect(
                'dashboard:specifications',
            )


def _deletespec(request):
    if request.method == 'POST':
        spec_id = request.POST['spec_id']
        #
        try:
            spec = Specification.objects.get(
                    user=request.user,
                    pk=spec_id
                )
            spec.deleted = True
            spec.save()
        except Exception:
            messages.add_message(
                    request,
                    messages.INFO,
                    'Something went wrong could not delete spec',
                    extra_tags='alert-warning specification'
                )
        else:
            messages.add_message(
                    request,
                    messages.INFO,
                    'Specification was binned but not permanently deleted.',
                    extra_tags='alert-success specification'
                )
        #
        return redirect(
                'dashboard:specifications',
            )


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


def _createmoduel(request):
    if request.method == 'POST':
        level = request.POST['level']
        subject = request.POST['subject']
        board = request.POST['board']
        name = request.POST['name']
        new_module = request.POST['new_module']
        Template = ContentTemplate.objects.get(
                name='Point'
            )
        #
        points = Point.objects.filter(
                user=request.user,
                p_level=level,
                p_subject=subject,
                p_moduel=new_module,
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
            my_point.p_content = Template.content
            my_point.p_unique_id = TagGenerator()
            my_point.save()
            #
            messages.add_message(
                    request,
                    messages.INFO,
                    'Successfully created a new moduel',
                    extra_tags='alert-success specmoduel'
                )
        else:
            messages.add_message(
                    request,
                    messages.INFO,
                    'Module Already exists, check your binned modules.',
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


def _renamemodule(request):
    if request.method == 'POST':
        level = request.POST['level']
        subject = request.POST['subject']
        module = request.POST['moduel']
        board = request.POST['board']
        name = request.POST['name']
        new_name = request.POST['new_name']
        points = Point.objects.filter(
                user=request.user,
                p_level=level,
                p_subject=subject,
                p_moduel=module
            )
        spec = Specification.objects.get(
                user=request.user,
                spec_level=level,
                spec_subject=subject,
                spec_board=board,
                spec_name=name,
            )
        if len(points) > 0:
            points.update(p_moduel=new_name)
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
                    extra_tags='alert-warning specchapter'
                )
        else:
            messages.add_message(
                    request,
                    messages.INFO,
                    'Something is wrong, please check that the input is correct.',
                    extra_tags='alert-warning specchapter'
            )
            kwargs = {
                'level': level,
                'subject': subject,
                'module': module,
                'board': board,
                'name': name,
            }
            return redirect(
                    'dashboard:specchapter',
                    **kwargs
                )
        kwargs = {
            'level': level,
            'subject': subject,
            'module': new_name,
            'board': board,
            'name': name,
        }
        return redirect(
                'dashboard:specchapter',
                **kwargs
            )


def _createchapter(request):
    if request.method == 'POST':
        level = request.POST['level']
        subject = request.POST['subject']
        module = request.POST['moduel']
        board = request.POST['board']
        name = request.POST['name']
        new_chapter = request.POST['new_chapter']
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
            my_point.p_content = Template.content
            my_point.p_unique_id = TagGenerator()
            my_point.save()
            #
            messages.add_message(
                    request,
                    messages.INFO,
                    'Successfully created a new chapter',
                    extra_tags='alert-success specchapter'
                )
        else:
            messages.add_message(
                    request,
                    messages.INFO,
                    'Chapter Already exists, check your binned chapters.',
                    extra_tags='alert-warning specchapter'
                )
        kwargs = {
            'level': level,
            'subject': subject,
            'module': module,
            'board': board,
            'name': name
        }
        return redirect(
                'dashboard:specchapter',
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
                    extra_tags='alert-warning specchapter'
                )
        else:
            messages.add_message(
                    request,
                    messages.INFO,
                    'Something is wrong, please check that the input is correct.',
                    extra_tags='alert-warning specchapter'
                )
        kwargs = {
            'level': level,
            'subject': subject,
            'module': module,
            'board': board,
            'name': name
        }
        return redirect(
                'dashboard:specchapter',
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
        new_name = request.POST['new_name']
        #
        points = Point.objects.filter(
                user=request.user,
                p_level=level,
                p_subject=subject,
                p_moduel=module,
                p_chapter=chapter,
            )
        spec = Specification.objects.get(
                user=request.user,
                spec_level=level,
                spec_subject=subject,
                spec_board=board,
                spec_name=name,
            )
        if len(points) > 0:
            points.update(p_chapter=new_name)
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
            'chapter': new_name,
            'board': board,
            'name': name,
        }
        return redirect(
                'dashboard:spectopic',
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
        new_topic = request.POST['new_topic']
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


def _renametopic(request):
    if request.method == 'POST':
        level = request.POST['level']
        subject = request.POST['subject']
        module = request.POST['moduel']
        chapter = request.POST['chapter']
        topic = request.POST['topic']
        board = request.POST['board']
        name = request.POST['name']
        new_name = request.POST['new_name']
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
        if len(points) > 0:
            points.update(p_topic=new_name)
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
                    f'Successfully Renamed the chapter: {topic} -> {new_name}',
                    extra_tags='alert-warning specpoint'
                )
        else:
            messages.add_message(
                    request,
                    messages.INFO,
                    'Something is wrong, please check that the input is correct.',
                    extra_tags='alert-warning specpoint'
            )
            kwargs = {
                'level': level,
                'subject': subject,
                'module': module,
                'chapter': chapter,
                'topic': topic,
                'board': board,
                'name': name,
            }
            return redirect(
                    'dashboard:specpoint',
                    **kwargs
                )
        kwargs = {
            'level': level,
            'subject': subject,
            'module': module,
            'chapter': chapter,
            'topic': new_name,
            'board': board,
            'name': name,
        }
        return redirect(
                'dashboard:specpoint',
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
        name = request.POST['name']
        new_point = request.POST['new_point']
        #
        Template = ContentTemplate.objects.get(
                name='Point'
            )
        Template.content['details']['hidden']['0']['point_title'] = new_point
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
        my_point.p_content = Template.content
        my_point.p_unique_id = TagGenerator()
        my_point.save()
        #
        messages.add_message(
                request,
                messages.INFO,
                'Successfully created a new point',
                extra_tags='alert-success specpoint'
            )
        kwargs = {
            'level': level,
            'subject': subject,
            'board': board,
            'module': moduel,
            'chapter': chapter,
            'topic': topic,
            'name': name
        }
        return redirect(
                'dashboard:specpoint',
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
                    extra_tags='alert-warning point'
                )
        else:
            messages.add_message(
                    request,
                    messages.INFO,
                    'Something is wrong, please check that the input is correct.',
                    extra_tags='alert-warning point'
                )
        kwargs = {
            'level': level,
            'subject': subject,
            'module': module,
            'chapter': chapter,
            'topic': topic,
            'board': board,
            'name': name
        }
        return redirect(
                'dashboard:specpoint',
                **kwargs
            )
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
                    extra_tags='alert-warning point'
                )
        else:
            messages.add_message(
                    request,
                    messages.INFO,
                    'Something is wrong, please check that the input is correct.',
                    extra_tags='alert-warning point'
                )
        kwargs = {
            'level': level,
            'subject': subject,
            'module': module,
            'chapter': chapter,
            'topic': topic,
            'board': board,
            'name': name
        }
        return redirect(
                'dashboard:specpoint',
                **kwargs
            )



def _savepointedit(request):
    if request.method == 'POST':
        point_id = request.POST['point_id']
        point = Point.objects.filter(user=request.user, pk=point_id)
        if len(point) == 1:
            form = MDEditorModleForm(request.POST, instance=point[0])
            if form.is_valid():
                form.save()
                content = form.cleaned_data['p_MDcontent'].split('```')
                hidden = content[1].split('yaml')[1]
                description = '```'.join(content[2:])
                #
                hidden_details = yaml.load(hidden.replace('\t', '  '))['hidden_details']
                title = hidden_details['point_title']
                vids = [(k.split('_')[1], i['video_title'], i['video_link']) for k, i in hidden_details.items() if 'vid' in k]
                vids_content = {str(int(k)-1): {'vid':{"vid_title": i,"vid_link": j}} for k,i,j in vids}
                #
                description_text = description.split('\n')
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
                point[0].p_content['details']['hidden']['0']['point_title'] = title
                point[0].p_content['details']['hidden']['0']['content'] = vids_content
                point[0].p_content['details']['description'] = description_content
                point[0].save()
                messages.add_message(
                        request,
                        messages.INFO,
                        'Saved !',
                        extra_tags='alert-success editorpoint'
                    )
            else:
                messages.add_message(
                        request,
                        messages.INFO,
                        'Something is wrong, please check that all inputs are valid.',
                        extra_tags='alert-danger editorpoint'
                    )
        else:
            messages.add_message(
                    request,
                    messages.INFO,
                    'Something is wrong, cannot find information.',
                    extra_tags='alert-danger editorpoint'
                )
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
    else:
        messages.add_message(
                request,
                messages.INFO,
                'Invalid Request Method',
                extra_tags='alert-danger home'
            )
        return redirect('main:index')


def _savequestionedit(request):
    if request.method == 'POST':
        question_id = request.POST['point_id']
        question = Question.objects.filter(user=request.user, pk=question_id)
        if len(question) == 1:
            form = MDEditorQuestionModleForm(request.POST, instance=question[0])
            if form.is_valid():
                form.save()
                content = form.cleaned_data['q_MDcontent'].split('+++')
                for details_part in content:
                    detail_items = details_part.split('\n')
                    if 'Meta_details' in detail_items[0]:
                        for sub_item in detail_items:
                            sub_item = sub_item.replace('\r','').replace('\n','')
                            if 'question_type' in sub_item:
                                question[0].q_content['details']['head']['0']\
                                        ['q_type'] = sub_item.replace('question_type: ', '')
                            if 'question_difficulty' in sub_item:
                                question[0].q_content['details']['head']['0']\
                                        ['q_difficulty'] = sub_item.replace('question_difficulty: ', '')
                    if 'Question' in detail_items[0]:
                        full_question = '\n'.join(detail_items[1:])
                        question_parts = full_question.split('PartName_')
                        n = 0
                        for part in question_parts:
                            if 'PartMark_' in part:
                                lines = part.split('\n')
                                details_line = lines[0].split('_')
                                part_name = details_line[0]
                                part_mark = details_line[-1].split(':')[0]
                                question[0].q_content['details']['questions']\
                                        [str(n)] = {}
                                #
                                question[0].q_content['details']['questions']\
                                        [str(n)]['q_part'] = part_name
                                question[0].q_content['details']['questions']\
                                        [str(n)]['q_part_mark'] = part_mark
                                n2 = 0
                                question[0].q_content['details']['questions']\
                                        [str(n)]['content'] = {}
                                for line in lines:
                                    if '!(' in line:
                                        first_list = line.split('(')[1].split(')')
                                        second_list = first_list[1].split('[')[1].split(']')
                                        item = {'img': {'img_info': first_list[0],'img_name': second_list[0]}}
                                        question[0].q_content['details']['questions']\
                                                [str(n)]['content'][str(n2)] = item
                                        n2 += 1
                                    elif 'PartMark' not in line:
                                        line = line.replace('\n','').replace('\r', '')
                                        if line != '':
                                            item = {'text': line}
                                            question[0].q_content['details']['questions']\
                                                    [str(n)]['content'][str(n2)] = item 
                                            n2 += 1
                                n += 1
                    if 'Answer' in detail_items[0]:
                        full_answer = '\n'.join(detail_items[1:])
                        answer_parts = full_answer.split('AnswerPart')
                        n = 0
                        for part in answer_parts:
                            if 'PartName_' in part:
                                lines = part.split('\n')
                                details_line = lines[0].split('_')
                                part_name = details_line[-1].replace('\r', '').replace('\n', '')
                                question[0].q_content['details']['answers']\
                                        [str(n)] = {}
                                #
                                question[0].q_content['details']['answers']\
                                        [str(n)]['q_part'] = part_name
                                n2 = 0
                                question[0].q_content['details']['answers']\
                                        [str(n)]['content'] = {}
                                for line in lines:
                                    if '!(' in line:
                                        first_list = line.split('(')[1].split(')')
                                        second_list = first_list[1].split('[')[1].split(']')
                                        item = {'img': {'img_info': first_list[0],'img_name': second_list[0]}}
                                        question[0].q_content['details']['answers']\
                                                [str(n)]['content'][str(n2)] = item
                                        n2 += 1
                                    elif 'PartName' not in line:
                                        line = line.replace('\n','').replace('\r', '')
                                        if line != '':
                                            item = {'text': line}
                                            question[0].q_content['details']['answers']\
                                                    [str(n)]['content'][str(n2)] = item 
                                            n2 += 1
                                n += 1
                question[0].save()
                messages.add_message(
                        request,
                        messages.INFO,
                        'Saved !',
                        extra_tags='alert-success editorquestion'
                    )
            else:
                messages.add_message(
                        request,
                        messages.INFO,
                        'Something is wrong, please check that all inputs are valid.',
                        extra_tags='alert-danger editorquestion'
                    )
        else:
            messages.add_message(
                    request,
                    messages.INFO,
                    'Something is wrong, cannot find information.',
                    extra_tags='alert-danger editorquestion'
                )
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
    else:
        messages.add_message(
                request,
                messages.INFO,
                'Invalid Request Method',
                extra_tags='alert-danger home'
            )
        return redirect('main:index')


def _createcustomtest(request):
    if request.method == 'POST':
        def clean(string):
            string = string.replace('[', '')
            string = string.replace(']', '')
            string = string.replace('"', '')
            string = string.replace(',', ' ')
            return string.split(' ')
        course_id = h_decode(clean(request.POST['course_id'])[0])
        #status_array = clean(request.POST['q_status_array'])
        #type_array = clean(request.POST['q_type_array'])
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
                    q_level=specification.spec_level,
                    q_subject=specification.spec_subject,
                )
        #
        #if status_array[0] != '0':
        #    all_tracked_questions = QuestionTrack.objects.filter(
        #                user=request.user,
        #                course=course,
        #            )
        #if type_array[0] != '0':
        #    question_pool = question_pool.filter(
        #            q_type__in=type_array
        #        )
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
        final_selection = question_pool[:10]
        paper_content = {i: question.id for i, question in enumerate(final_selection)}
        paper = UserPaper.objects.create(
                user=request.user,
                pap_course=course,
                pap_info=paper_content
                )
        #
        return JsonResponse({'res': 1, 'paper_id': h_encode(paper.id)})
    else:
        return JsonResponse({'res': 0})
