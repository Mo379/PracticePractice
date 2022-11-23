import pandas as pd
from collections import OrderedDict
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.functional import cached_property
from django.contrib import messages
from django.views import generic
from content.util.GeneralUtil import (
        TagGenerator,
        insert_new_spec_order,
        order_full_spec_content,
    )
from view_breadcrumbs import BaseBreadcrumbMixin
from django.forms import model_to_dict
from content.models import *
from content.forms import MDEditorModleForm
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
                try:
                    spec = Specification.objects.get(
                            spec_level=subject['p_level'],
                            spec_subject=subject['p_subject'],
                            spec_board='Universal',
                            spec_name='Universal',
                        )
                except:
                    continue
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


def _renamecourse(request):
    if request.method == 'POST':
        course_name = request.POST['new_name']
        course_id = request.POST['course_id']
        courses = Course.objects.filter(
                user=request.user,
                pk=course_id
            )
        #
        if len(courses) == 1:
            try:
                course = courses[0]
                course.course_name = course_name
                course.save()
            except Exception:
                messages.add_message(
                        request,
                        messages.INFO,
                        'Something went wrong could not update course.',
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


def _updatecoursesummary(request):
    if request.method == 'POST':
        course_id = request.POST['course_id']
        course_summary = request.POST['course_summary']
        courses = Course.objects.filter(
                user=request.user,
                pk=course_id
            )
        #
        if len(courses) == 1:
            try:
                course = courses[0]
                course.course_summary = course_summary
                course.save()
            except Exception:
                messages.add_message(
                        request,
                        messages.INFO,
                        'Something went wrong could not update course.',
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
                    'Input can only be alphanumeric!',
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
