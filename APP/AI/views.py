import re
import time
import collections
import json
from cryptography.fernet import Fernet
from collections import defaultdict
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import redirect
from django.contrib import messages
from django.conf import settings
from django.contrib.auth.decorators import login_required
from braces.views import (
        LoginRequiredMixin,
        GroupRequiredMixin,
        SuperuserRequiredMixin,
    )
from PP2.mixin import (
        AnySubscriptionRequiredMixin,
        AnySubscriptionRequiredDec,
        AISubscriptionRequiredMixin,
        AISubscriptionRequiredDec,
        CourseSubscriptionRequiredMixin,
        CourseSubscriptionRequiredDec,
        AuthorRequiredMixin,
        AuthorRequiredDec,
        AffiliateRequiredMixin,
        AffiliateRequiredDec,
        TrusteeRequiredMixin,
        TrusteeRequiredDec
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
        Lesson_part,
        Lesson_quiz,
    )
from user.forms import (
        AppearanceChoiceForm,
    )
from content.util.GeneralUtil import (
        order_live_spec_content,
        TagGenerator,
        increment_course_subscription_significant_click
    )
from PP2.utils import h_encode, h_decode
from django.http import JsonResponse
from AI.functions import create_quiz_function, create_course_questions
from AI import functions_endpoint
from management.templatetags.general import ToMarkdownManual


# Create your views here.
class AIView(
        AISubscriptionRequiredMixin,
        CourseSubscriptionRequiredMixin,
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
        #
        course = Course.objects.get(pk=course_id)
        course_subscription = CourseSubscription.objects.filter(
                user=self.request.user,
                course=course
            )
        course_subscription = course_subscription[0]
        #
        if module not in course_subscription.progress_track.keys():
            course_subscription.progress_track[module] = {}
        if chapter not in course_subscription.progress_track[module].keys():
            course_subscription.progress_track[module][chapter] = {}
        if 'content' not in course_subscription.progress_track[module][chapter].keys():
            course_subscription.progress_track[module][chapter]['content'] = True
        course_subscription.save()
        # Get course modules and chapters
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
        num_next_points = 0
        lesson_parts = []
        last_item = ''
        breaker = False
        quizzes_states = {}

        def extract_thread_quizes(chat):
            """Extract the quizs from the thread"""
            quizzes = {}
            for part in chat.keys():
                if 'thread' in chat[part].keys():
                    thread = chat[part]['thread']
                    for item in thread:
                        if item['role'] == 'function':
                            if item['name'] == 'create_a_quiz':
                                content = json.loads(item['content'])
                                content['user_answers'] = content['user_answers'] if 'user_answers' in content.keys() else {}
                                solutions = {}
                                answers = {}
                                for question in content['quiz'].keys():
                                    solutions[f'{question}'] = content['quiz'][question]['answer']['correct_choice']
                                    answers[f'{question}'] = content['quiz'][question]['answer']['answer']
                                completed = False
                                percentage_score = False
                                if len(solutions) == len(content['user_answers']):
                                    def compare_dictionaries(dict1, dict2):
                                        num_matches = 0
                                        for key in dict1.keys():
                                            if key in dict2:
                                                if dict1[key] == dict2[key]:
                                                    num_matches += 1
                                        return num_matches
                                    completed = True
                                    percentage_score = 100*(compare_dictionaries(solutions, content['user_answers'])/len(solutions))
                                questions = {}
                                for key in solutions.keys():
                                    user_answer = content['user_answers'][key] if key in content['user_answers'].keys() else None
                                    questions[key] = {
                                            "user_answer": user_answer,
                                            "correct_choice": solutions[key],
                                            "is_correct": True if user_answer == solutions[key] else False,
                                            "answer": answers[key],
                                        }
                                quizzes[content['unique_id']] = {
                                        "quiz": questions,
                                        "is_completed": completed,
                                        "percentage_score": percentage_score
                                    }
            return quizzes
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
                if len(lesson_parts) > 0:
                    system_chats_in_part = 0
                    for chat in lesson_parts[-1].part_chat:
                        if 'system' in lesson_parts[-1].part_chat[chat].keys():
                            system_chats_in_part += 1
                    num_next_points += len(lesson_parts[-1].part_content['content'].keys()) - system_chats_in_part
            if breaker:
                num_next_points += len(part.part_content['content'].keys())
            quizzes_states.update(extract_thread_quizes(part.part_chat))
            lesson_parts.append(part)
        #
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
        context['coursesubscription'] = course_subscription
        context['form_appearancechoice'] = appearancechoiceform
        context['course'] = course
        context['course_version'] = latest_course_version
        context['lesson'] = active_lesson
        context['lesson_parts'] = lesson_parts
        context['quizzes'] = quizzes_states
        context['last_item'] = last_item
        context['num_next_points'] = num_next_points
        #
        context['module'] = module
        context['previous_chapter'] = previous_chapter
        context['next_chapter'] = next_chapter
        return context


@CourseSubscriptionRequiredDec
@AISubscriptionRequiredDec
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


@CourseSubscriptionRequiredDec
@AISubscriptionRequiredDec
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
        try:
            significant_click_name = 'ai_next_point'
            increment_course_subscription_significant_click(
                    request.user, lesson_part.lesson.course, significant_click_name
            )
        except Exception as e:
            print(str(e))
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
                content_html, video_html, script_html, video_tags = ToMarkdownManual('', point_obj.id)
                response = {
                        'error': 0,
                        'message': content_html,
                        'videos_html': video_html,
                        'script_html': script_html,
                        'videos_tags': video_tags,
                        'new_tag': TagGenerator(),
                        'new_point_id': point_obj.id,
                        'new_point_unique': next_point,
                        'relevant_part_id': lesson_part.id,
                        'new_topic': new_topic,
                    }
                return JsonResponse(response)
    return JsonResponse({'error': 1, 'message': 'Something went wrong, please try again.'})


@AISubscriptionRequiredDec
def _ask_from_book(request):
    if request.method == 'POST':
        lesson_part_id = request.POST['part_id']
        point_id = request.POST['point_id']
        global_order_id = request.POST['global_order_id']
        local_order_id = request.POST['local_order_id']
        user_prompt = request.POST['user_prompt']
        prompt_type_value = request.POST['prompt_type_value']
        #
        lesson_part = Lesson_part.objects.get(pk=lesson_part_id)
        try:
            significant_click_name = 'ai_ask_from_book'
            increment_course_subscription_significant_click(
                    request.user, lesson_part.lesson.course, significant_click_name
            )
        except Exception as e:
            print(str(e))
        #
        chat_subthread_number = str(int(global_order_id)-1)
        part = lesson_part.part_chat[chat_subthread_number]
        point_obj = Point.objects.get(p_unique_id=part['system'])
        system_content, video_html, script_html, video_tags = ToMarkdownManual('', point_obj.id)
        system_content = re.sub('<[^<]+?>', '', system_content)
        #
        lambda_url = settings.CHATGPT_LAMBDA_URL
        #
        chat = part['thread'][0:int(local_order_id)*2] if 'thread' in part.keys() else []
        #
        message = {
          "chat": [
            {
              "role": "system",
              "content": f"Youre a helpful tutor for this student. Your responses are formatted in HTML and MATHJAX ($ for inline maths), the lesson being taught is the following {system_content}."
            },
            *chat,
            {
              "role": "user",
              "content": str(user_prompt)
            }
          ]
        }
        lesson_part.save()
        #
        function_app_endpoint = {
                'return_url': f"{settings.SITE_URL}/AI/_function_app_endpoint",
                'user_prompt': str(user_prompt),
                'unique_id': TagGenerator()
            }
        #
        if int(prompt_type_value) == 1:
            quiz_function = create_quiz_function(5)
            functions = [quiz_function[0]]
            function_call = {"name": quiz_function[1]}
            function_app_endpoint['prompt_type_value'] = prompt_type_value
            message['chat'][0]['content'] = quiz_function[2] + f" {system_content}"
        elif int(prompt_type_value) == 2:
            functions = None
            function_call = None
            function_app_endpoint['prompt_type_value'] = prompt_type_value
        elif int(prompt_type_value) == 3:
            functions = None
            function_call = None
            function_app_endpoint['prompt_type_value'] = prompt_type_value
        else:
            functions = None
            function_call = None
            function_app_endpoint['prompt_type_value'] = prompt_type_value

        #
        response = {
                'error': 0,
                'message': message,
                'functions': functions,
                'function_call': function_call,
                'function_app_endpoint': function_app_endpoint,
                'lambda_url': lambda_url,
            }
        return JsonResponse(response)
    return JsonResponse({'error': 1, 'message': 'Something went wrong, please try again.'})


@csrf_exempt
def _function_app_endpoint(request):
    if request.method == 'POST':
        json_data = json.loads(request.body)
        if json_data['auth_key'] == settings.OPENAI_ORG:
            if json_data['ai_function_name']:
                function_name = json_data['ai_function_name']
                if function_name in ['create_a_quiz', 'create_flashcards', 'create_essay']:
                    response = functions_endpoint.lesson_prompts(
                            request,
                            json_data
                        )
                elif function_name == 'create_course_introduction':
                    response = functions_endpoint.course_introduction_prompts(
                            request,
                            json_data
                        )
                elif function_name == 'create_course_questions':
                    response = functions_endpoint.course_questions_prompts(
                            request,
                            json_data
                        )
                elif function_name == 'create_course_point':
                    pass
                elif function_name == 'send_email':
                    pass
            else:
                response = functions_endpoint.lesson_prompts(
                        request,
                        json_data
                    )
                
            #
            return JsonResponse(response)
        else:
            return JsonResponse({'status_code': 500, 'message': 'Internal Server Error.'})
    else:
        return JsonResponse({'status_code': 500, 'message': 'Internal Server Error.'})


@AISubscriptionRequiredDec
def _mark_quiz_question(request):
    if request.method == 'POST':
        lesson_part_id = request.POST['lesson_part_id']
        quiz_id = request.POST['quiz_id']
        quiz_question_number = request.POST['question_number']
        user_choice = request.POST['user_answer']
        #
        lesson_part = Lesson_part.objects.get(pk=lesson_part_id)
        #
        try:
            significant_click_name = 'ai_mark_quiz_question'
            increment_course_subscription_significant_click(
                    request.user, lesson_part.lesson.course, significant_click_name
            )
        except Exception as e:
            print(str(e))
        #
        try:
            lesson_quiz, created = Lesson_quiz.objects.get_or_create(
                    user=request.user,
                    course=lesson_part.lesson.course,
                    lesson_part=lesson_part,
                    quiz_id=quiz_id,
                )
            #

            def reinject_user_response_to_thread(chat, quiz_id, user_answers):
                """Extract the quiz from the thread using the quiz id"""
                for part in chat.keys():
                    if 'thread' in chat[part].keys():
                        thread = chat[part]['thread']
                        for idd, item in enumerate(thread):
                            if item['role'] == 'function':
                                if item['name'] == 'create_a_quiz':
                                    content = json.loads(item['content'])
                                    if content['unique_id'] == quiz_id:
                                        content['user_answers'] = user_answers
                                        chat[part]['thread'][idd]['content'] = json.dumps(content)
                                        return chat
            if created:
                def extract_thread_quiz(chat, quiz_id):
                    """Extract the quiz from the thread using the quiz id"""
                    for part in chat.keys():
                        if 'thread' in chat[part].keys():
                            thread = chat[part]['thread']
                            for item in thread:
                                if item['role'] == 'function':
                                    if item['name'] == 'create_a_quiz':
                                        content = json.loads(item['content'])
                                        if content['unique_id'] == quiz_id:
                                            return content
                extracted_quiz = extract_thread_quiz(
                        lesson_part.part_chat,
                        quiz_id
                    )
                lesson_quiz.quiz = extracted_quiz
                lesson_quiz.save()

            if quiz_question_number not in lesson_quiz.user_answers.keys():
                lesson_quiz.user_answers[quiz_question_number] = user_choice
                lesson_part.part_chat = reinject_user_response_to_thread(
                        lesson_part.part_chat,
                        quiz_id,
                        lesson_quiz.user_answers
                    )
                lesson_part.save()
            solutions = {}
            for question in lesson_quiz.quiz['quiz'].keys():
                solutions[f'{question}'] = lesson_quiz.quiz['quiz'][question]['answer']['correct_choice']
            lesson_quiz.save()
        except Exception as e:
            response = {
                    'status_code': 500,
                    'message': 'Internal Server Error.'
                }
        else:
            is_correct = False
            completed = False
            percentage_score = False
            answer = lesson_quiz.quiz['quiz'][quiz_question_number]['answer']['answer']
            correct_choice = solutions[quiz_question_number]
            #
            if len(solutions) == len(lesson_quiz.user_answers):
                def compare_dictionaries(dict1, dict2):
                    num_matches = 0
                    for key in dict1.keys():
                        if key in dict2:
                            if dict1[key] == dict2[key]:
                                num_matches += 1
                    return num_matches
                completed = True
                percentage_score = 100*(compare_dictionaries(solutions, lesson_quiz.user_answers)/len(solutions))
                lesson_quiz.completed = True
                lesson_quiz.percentage_score = percentage_score
                lesson_quiz.save()
            #
            if solutions[quiz_question_number] == lesson_quiz.user_answers[quiz_question_number]:
                is_correct = True
            #
            response = {
                    'status_code': 200,
                    'message': 'Sucess',
                    'is_correct': is_correct,
                    'completed': completed,
                    'percentage_score': percentage_score,
                    'answer': answer,
                    'correct_choice': correct_choice,
                }
        #
        return JsonResponse(response)
    return JsonResponse({'status_code': 500, 'message': 'Internal Server Error.'})


@AuthorRequiredDec
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
        try:
            job = ContentGenerationJob.objects.create(
                    user=request.user,
                    specification=spec,
                    moduel=module,
                    chapter=chapter,
                )
            #_generate_course_content.delay(job.id)
        except Exception:
            #
            messages.add_message(
                    request,
                    messages.INFO,
                    f'Something went wrong, the job cannot be created.',
                    extra_tags='alert-info spectopic'
                )
            return redirect(
                    'dashboard:spectopic',
                    **kwargs
                )
        else:
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


@AuthorRequiredDec
def _savepromptquestion(request):
    if request.method == 'POST':
        q_prompt_id = request.POST['q_prompt_id']
        q_prompt = request.POST['q_prompt']
        #
        prompt = ContentPromptQuestion.objects.get(user=request.user, pk=q_prompt_id)
        prompt.prompt = q_prompt
        prompt.save()
        #
        lambda_url = settings.CHATGPT_LAMBDA_URL
        #
        message = {
          "chat": [
            {
              "role": "system",
              "content": "Placeholder"
            },
            {
              "role": "user",
              "content": 'Please generate those questions'
            }
          ]
        }
        function_app_endpoint = {
                'return_url': f"{settings.SITE_URL}/AI/_function_app_endpoint",
                'q_prompt_id': q_prompt_id
            }
        #
        quiz_function = create_course_questions(q_prompt, prompt, 5)
        functions = [quiz_function[0]]
        function_call = {"name": quiz_function[1]}
        message['chat'][0]['content'] = quiz_function[2]

        #
        response = {
                'error': 0,
                'message': message,
                'functions': functions,
                'function_call': function_call,
                'function_app_endpoint': function_app_endpoint,
                'lambda_url': lambda_url,
            }
        return JsonResponse(response)
    return JsonResponse({'error': 1, 'message': 'Error'})


@AuthorRequiredDec
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


@AuthorRequiredDec
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
