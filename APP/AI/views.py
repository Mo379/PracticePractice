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
from content.models import Course, CourseSubscription, CourseVersion, Specification, Point
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
        order_live_spec_content,
        TagGenerator
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
        latest_course_version = CourseVersion.objects.filter(
                    course=course
                ).order_by('-version_number')[0]
        spec_content = latest_course_version.version_content
        #
        ordered_content = order_live_spec_content(spec_content)
        content = ordered_content[module]['content'][chapter]['content']
        topics = list(content.keys())
        active_lesson, _ = Lesson.objects.get_or_create(
                user=user,
                course=course,
                moduel=module,
                chapter=chapter,
            )
        #
        list_chapters = list(ordered_content[module]['content'].keys())
        chapter_index = list_chapters.index(chapter)
        previous_chapter = list_chapters[chapter_index-1] if chapter_index -1 >= 0 else None
        next_chapter = list_chapters[chapter_index+1] if chapter_index +1 < len(list_chapters) else None
        #
        lesson_parts = []
        last_item = ''
        breaker = False
        for topic in topics:
            part, created = Lesson_part.objects.get_or_create(
                    user=user,
                    lesson=active_lesson,
                    topic=topic,
                    part_content=content[topic]
                )
            if len(part.part_chat) == 0 and breaker == False:
                breaker = True
                last_part = lesson_parts[-1] if len(lesson_parts) > 0 else part
                last_item_index = len(last_part.part_chat) -1 if len(lesson_parts) > 0 else 0
                last_item = f'{last_part.topic}-{last_item_index}'
            lesson_parts.append(part)

        #
        course_subscription = CourseSubscription.objects.filter(
                user=self.request.user,
                course=course
            )
        #
        if len(lesson_parts[0].part_chat.keys()) == 0:
            first_point = list(lesson_parts[0].part_content['content'].keys())[0]
            lesson_parts[0].part_chat = {
                    "0": {
                            'system': first_point, 'title': lesson_parts[0].topic
                        }
                }
            lesson_parts[0].save()
        #
        context['coursesubscription'] = course_subscription if len(course_subscription) == 1 else False
        context['form_appearancechoice'] = appearancechoiceform
        context['course'] = course
        context['course_version'] = latest_course_version
        context['lesson'] = active_lesson
        context['lesson_parts'] = lesson_parts
        context['last_item'] = last_item
        #
        context['module'] = module
        context['previous_chapter'] = previous_chapter
        context['next_chapter'] = next_chapter
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


def _next_point(request):
    if request.method == 'POST':
        course_version_id = request.POST['course_version_id']
        lesson_part_id = request.POST['part_id']
        point_id = request.POST['point_id']
        #
        lesson_part = Lesson_part.objects.get(pk=lesson_part_id)
        part_content = lesson_part.part_content['content']
        previous_point_pos = int(part_content[point_id]['position'])
        #
        latest_course_version = CourseVersion.objects.get(
                    id=course_version_id
                )
        spec_content = latest_course_version.version_content
        #
        ordered_content = order_live_spec_content(spec_content)
        content = ordered_content[lesson_part.lesson.moduel]['content'][lesson_part.lesson.chapter]['content']
        topics = list(content.keys())
        #
        next_point = None
        new_topic = None
        if previous_point_pos >= len(part_content)-1:
            next_point = None
            if topics.index(lesson_part.topic) < len(topics)-1:
                lesson_part = Lesson_part.objects.get(
                        user=request.user,
                        lesson=lesson_part.lesson,
                        topic=topics[topics.index(lesson_part.topic)+1]
                        )
                for point in lesson_part.part_content['content']:
                    if int(lesson_part.part_content['content'][point]['position']) == 0:
                        next_point = point
                        new_topic = lesson_part.topic
        else:
            for point in part_content:
                if int(part_content[point]['position']) == previous_point_pos + 1:
                    next_point = point
        #
        if next_point is None:
            return JsonResponse({'error': 1, 'message': 'Point does not exits!'})
        else:
            try:
                point_obj = Point.objects.get(p_unique_id=next_point)
                new_pos = len(lesson_part.part_chat.keys())
                lesson_part.part_chat[f"{str(new_pos)}"] = {
                        'system': next_point
                    }
                lesson_part.save()
            except Exception:
                return JsonResponse({'error': 1, 'message': 'Point does not exits!'})
            else:
                from management.templatetags.general import ToMarkdownManual
                content_html, video_html, script_html, video_tags = ToMarkdownManual('', point_obj.id)
                response = {
                        'error': 0,
                        'message': content_html,
                        'videos_html': video_html,
                        'script_html': script_html,
                        'videos_tags': video_tags,
                        'new_tag': TagGenerator(),
                        'new_point_id': next_point,
                        'relevant_part_id': lesson_part.id,
                        'new_topic': new_topic,
                    }
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
        _generate_course_content.delay(job.id)
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
