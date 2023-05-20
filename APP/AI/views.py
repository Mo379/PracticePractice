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
from content.models import Course, CourseSubscription, Specification
from user.models import (
        User
    )
from AI.models import (
        ContentGenerationJob,
        ContentPromptQuestion,
        ContentPromptTopic,
        ContentPromptPoint,
        Lesson,
        Lesson_part
    )
from user.forms import (
        AppearanceChoiceForm,
    )
from content.util.GeneralUtil import (
        order_live_spec_content
    )
from PP2.utils import h_encode, h_decode
from django.http import JsonResponse
from AI.tasks import _generate_course_content



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
        course_subscription = CourseSubscription.objects.filter(
                user=self.request.user,
                course=course
                )
        #
        context['coursesubscription'] = course_subscription if len(course_subscription) else False
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
        if created:
            response['introduction'] = lesson_part.part_introduction
        return JsonResponse(response)
    return JsonResponse({'error': 1, 'message': 'Something went wrong, please try again.'})


def _newgenerationjob(request):
    if request.method == 'POST':
        spec_id = request.POST['spec_id']
        module = request.POST['moduel']
        chapter = request.POST['chapter']
        #
        spec = Specification.objects.get(pk=spec_id)
        kwargs = {
            'level': spec.spec_level,
            'subject': spec.spec_subject,
            'module': module,
            'chapter': chapter,
            'board': spec.spec_board,
            'name': spec.spec_name,
        }
        #
        q_prmpts = ContentPromptQuestion.objects.filter(
                user=request.user,
                specification=spec,
                moduel=module,
                chapter=chapter,
                activated=True,
            )
        p_prmpts = ContentPromptPoint.objects.filter(
                user=request.user,
                specification=spec,
                moduel=module,
                chapter=chapter,
                activated=True,
            )
        generation_jobs = ContentGenerationJob.objects.filter(
                user=request.user,
                specification=spec,
                moduel=module,
                chapter=chapter,
            ).order_by('-created_at')
        if len(generation_jobs) > 0:
            last_job = generation_jobs[0]
        else:
            last_job = False
        if last_job:
            if last_job.finished == False:
                messages.add_message(
                        request,
                        messages.INFO,
                        f'Your job will begin shortly please check back after a few minutes!',
                        extra_tags='alert-info spectopic'
                    )
                return redirect(
                        'dashboard:spectopic',
                        **kwargs
                    )
        if len(q_prmpts) + len(p_prmpts) < 1:
            messages.add_message(
                    request,
                    messages.INFO,
                    f'You need to activate at least one question or point prompt.',
                    extra_tags='alert-warning spectopic'
                )
            return redirect(
                    'dashboard:spectopic',
                    **kwargs
                )
        job = ContentGenerationJob.objects.create(
                user=request.user,
                specification=spec,
                moduel=module,
                chapter=chapter,
            )
        _generate_course_content(job.id)
        #
        messages.add_message(
                request,
                messages.INFO,
                f'Your job will begin shortly please check back after a few minutes!',
                extra_tags='alert-info spectopic'
            )
        return redirect(
                'dashboard:spectopic',
                **kwargs
            )
    return redirect(
            'dashboard:specifications',
        )


def _savepromptquestion(request):
    if request.method == 'POST':
        q_prompt_id = request.POST['q_prompt_id']
        q_prompt = request.POST['q_prompt']
        activated = True if request.POST['activated'] == 'true' else False
        #
        prompt = ContentPromptQuestion.objects.get(pk=q_prompt_id)
        prompt.prompt = q_prompt
        prompt.activated = activated
        prompt.save()
        return JsonResponse({'error': 0, 'message': 'Saved'})
    return JsonResponse({'error': 1, 'message': 'Error'})


def _saveprompttopic(request):
    if request.method == 'POST':
        t_prompt_id = request.POST['t_prompt_id']
        t_prompt = request.POST['t_prompt']
        #
        prompt = ContentPromptTopic.objects.get(pk=t_prompt_id)
        prompt.prompt = t_prompt
        prompt.save()
        return JsonResponse({'error': 0, 'message': 'Saved'})
    return JsonResponse({'error': 1, 'message': 'Error'})


def _savepromptpoint(request):
    if request.method == 'POST':
        p_prompt_id = request.POST['p_prompt_id']
        p_prompt = request.POST['p_prompt']
        activated = True if request.POST['activated'] == 'true' else False
        #
        prompt = ContentPromptPoint.objects.get(pk=p_prompt_id)
        prompt.prompt = p_prompt
        prompt.activated = activated
        prompt.save()
        return JsonResponse({'error': 0, 'message': 'Saved'})
    return JsonResponse({'error': 1, 'message': 'Error'})
