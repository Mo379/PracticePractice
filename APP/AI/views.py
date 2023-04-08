import collections
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
from AI.models import Lesson
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
        user = User.objects.get(pk=self.request.user.id)
        appearancechoiceform = AppearanceChoiceForm(instance=user)
        # Get course modules and chapters
        course = Course.objects.get(pk=course_id)
        spec = course.specification
        content = order_live_spec_content(spec.spec_content)
        modules = list(content.keys())
        active_lessons = Lesson.objects.filter(
                user=user,
                course=course,
            ).order_by('-created_at')
        claimed_lessons = {lesson.moduel for lesson in active_lessons}
        #
        context['form_appearancechoice'] = appearancechoiceform
        context['course'] = course
        context['modules'] = modules
        context['lessons'] = active_lessons
        context['claimed_lessons'] = claimed_lessons
        return context


@login_required(login_url='/user/login', redirect_field_name=None)
def _themechange(request):
    if request.method == 'POST':
        form = AppearanceChoiceForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.add_message(
                    request,
                    messages.INFO,
                    'Your preferred theme was successfully updated ' +
                    '(Try to refresh your browser if no changes show).',
                    extra_tags='alert-success AI_window'
                )
        else:
            messages.add_message(
                    request,
                    messages.INFO,
                    'Something is wrong, please check that all inputs are valid.'+str(form.errors),
                    extra_tags='alert-danger AI_window'
                )
    else:
        messages.add_message(
                request,
                messages.INFO,
                'Invalid Request Method',
                extra_tags='alert-danger AI_window'
            )
    return redirect('AI:index')


@login_required(login_url='/user/login', redirect_field_name=None)
def _start_new_lesson(request):
    if request.method == 'POST':
        user = request.user
        course_id = h_decode(request.POST['course_id'])
        lesson_module = request.POST['lesson_module']
        kwargs = {
            'course_id': course_id
        }
        #
        try:
            course = Course.objects.get(pk=course_id)
        except Exception:
            messages.add_message(
                    request,
                    messages.INFO,
                    'Course does not exist!',
                    extra_tags='alert-danger AI_window'
                )
            return redirect(
                    'content:content',
                )
        content = course.specification.spec_content
        try:
            module_content = content[lesson_module]
        except Exception:
            messages.add_message(
                    request,
                    messages.INFO,
                    'The input options are not available valid.',
                    extra_tags='alert-danger CollaborationTasks'
                )
            return redirect(
                    'AI:index',
                    **kwargs
                )
        # Check if task is duplicate
        check_lessons = Lesson.objects.filter(
                user=user,
                course=course,
                moduel=lesson_module
                )
        if len(check_lessons) == 0:
            Lesson.objects.create(
                    user=user,
                    course=course,
                    moduel=lesson_module,
                    lesson_content=module_content
                )
            messages.add_message(
                    request,
                    messages.INFO,
                    'Your lesson has been created!',
                    extra_tags='alert-success AI_window'
                )
        else:
            messages.add_message(
                    request,
                    messages.INFO,
                    'This lesson has already been started.',
                    extra_tags='alert-warning AI_window'
                )
        return redirect(
                'AI:index',
                **kwargs
            )
    return redirect(
            'content:content',
        )


@login_required(login_url='/user/login', redirect_field_name=None)
def _load_lesson(request):
    if request.method == 'POST':
        lesson_id = h_decode(request.POST['lesson_id'])
        #
        try:
            lesson = Lesson.objects.get(pk=lesson_id)
        except Exception:
            return JsonResponse({'error': 1, 'message': 'Lesson does not exits!'})
        chat = lesson.lesson_chat
        content = lesson.lesson_content
        return JsonResponse({'error': 0, 'chat': chat, 'content': content})
    return JsonResponse({'error': 1, 'message': 'Something went wrong, please try again.'})
