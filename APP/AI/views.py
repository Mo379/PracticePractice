import collections
from collections import defaultdict
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from braces.views import (
        LoginRequiredMixin,
        GroupRequiredMixin,
        SuperuserRequiredMixin,
    )
from django.views import generic
from content.models import Course
from user.models import (
        User
    )
from AI.models import Lesson, Lesson_part
from user.forms import (
        AppearanceChoiceForm,
    )
from content.util.GeneralUtil import (
        order_live_spec_content
    )
from PP2.utils import h_encode, h_decode
from django.http import JsonResponse



# Create your views here.
class AIView(
        LoginRequiredMixin,
        generic.ListView
        ):
    login_url = 'user:login'
    redirect_field_name = False
    template_name = 'AI/AI.html'
    context_object_name = 'context'

    def get_queryset(self):
        """Return all of the required hub information"""
        context = {}
        course_id = self.kwargs['course_id']
        module = self.kwargs['module']
        chapter = self.kwargs['chapter']
        user = User.objects.get(pk=self.request.user.id)
        appearancechoiceform = AppearanceChoiceForm(instance=user)
        # Get course modules and chapters
        course = Course.objects.get(pk=course_id)
        spec = course.specification
        content = order_live_spec_content(spec.spec_content)[module]['content'][chapter]['content']
        topics = list(content.keys())
        active_lesson, created = Lesson.objects.get_or_create(
                user=user,
                course=course,
                module=module,
                chapter=chapter,
            )
        if created:
            active_lesson.lesson_content = course.specification.spec_content
            active_lesson.save()
        for topic in topics:
            started_lesson_parts = Lesson_part.objects.filter(
                    user=user,
                    lesson=active_lesson
                )

        # create a defaultdict with default value as an empty list
        lesson_parts_holder = defaultdict(list)
        for part in started_lesson_parts:
            lesson_parts_holder[part.lesson.moduel].append(part.chapter)

        chapters = collections.OrderedDict({})
        for module in modules:
            _chapters = list(content[module]['content'].keys())
            chapters[module] = _chapters
        #
        context['form_appearancechoice'] = appearancechoiceform
        context['course'] = course
        context['modules'] = modules
        context['chapters'] = chapters
        context['started_chapters'] = lesson_parts_holder
        context['lessons'] = active_lessons
        return context


@login_required(login_url='/user/login', redirect_field_name=None)
def _load_lesson(request):
    if request.method == 'POST':
        user = request.user
        lesson_id = h_decode(request.POST['lesson_id'])
        lesson = Lesson.objects.get(pk=lesson_id)
        chapter = request.POST['chapter']
        #
        try:
            lesson_part, created = Lesson_part.objects.get_or_create(
                    user=user,
                    lesson=lesson,
                    chapter=chapter
                )
        except Exception:
            return JsonResponse({'error': 1, 'message': 'Lesson does not exits!'})
        part_chat = lesson_part.part_content
        response = {'error': 0, 'chat': part_chat}
        print(created)
        if created:
            response['introduction'] = lesson_part.part_introduction
        return JsonResponse(response)
    return JsonResponse({'error': 1, 'message': 'Something went wrong, please try again.'})
