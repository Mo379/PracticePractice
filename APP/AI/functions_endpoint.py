import time
from django.conf import settings
import json
from PP2.utils import fire_and_forget
from AI.models import Lesson_part, ContentPromptQuestion, ContentPromptPoint
from AI import workflows
from AI.functions import (
    general_function_call,
    create_course_outline
)
from content.models import Course, Question, Point


def course_outline_prompts(request, json_data):
    #
    course_id = json_data['course_id']
    course = Course.objects.get(pk=course_id)
    nth_reflection = json_data['nth_reflection']
    #
    try:
        if nth_reflection == 5 or len(course.specification.spec_content.keys()) > 0:
            if 'ai_response' in json_data.keys():
                modules = json.loads(json_data['ai_response'])['modules'].split(',')
                modules = [s.strip() for s in modules]
                spec_content = {}
                for idd, module in enumerate(modules):
                    spec_content[module] = {
                            'active': True,
                            'content': {},
                            'position': idd+1
                        }
                course.specification.spec_content = spec_content
                course.specification.save()
                nth_reflection = 0
            for module in course.specification.spec_content.keys():
                courseChapterOutline_function = create_course_outline(
                        course,
                        item_type='chapter',
                        current_module=module,
                    )
                lambda_url = settings.CHATGPT_LAMBDA_URL
                function_app_endpoint = {
                        'return_url': f"{settings.SITE_URL}/AI/_function_app_endpoint",
                        'course_id': course.id,
                        'nth_reflection': 0,
                        'type': 'chapter',
                        'module': module,
                        'model_name': 'gpt-3.5-turbo-0613',
                        'model_name': 'gpt-4-0613'
                    }
                user_prompt = """With the information provided for this
                          course, please continue or start creating the outline.
                          if previous ouputs have been presented please attempt to
                          reorder and improve them. This outline is for the
                          provided module, please give a list of chapters.
                          """
                request_body, headers = general_function_call(courseChapterOutline_function, function_app_endpoint, user_prompt)
                if len(course.specification.spec_content[module]['content']) == 0:
                    print(f'fire for {module}')
                    time.sleep(25)
                    fire_and_forget(lambda_url, request_body, headers)
                else:
                    print(f'pass for {module}')
                    course_outlineChapter_prompts('', {'course_id': course.id, 'nth_reflection': 0, 'module': module})
        else:
            if 'ai_response' in json_data.keys():
                modules = json.loads(json_data['ai_response'])['modules'].split(',')
                modules = [s.strip() for s in modules]
            else:
                modules = ''
            #
            courseOutline_function = create_course_outline(course, previous_output=modules, item_type='module')
            lambda_url = settings.CHATGPT_LAMBDA_URL
            function_app_endpoint = {
                    'return_url': f"{settings.SITE_URL}/AI/_function_app_endpoint",
                    'course_id': course.id,
                    'nth_reflection': nth_reflection+1,
                    'type': 'module',
                    'model_name': 'gpt-3.5-turbo-0613',
                    'model_name': 'gpt-4-0613'
                }
            user_prompt = """With the information provided for this
                      course, please continue or start creating the outline.
                      if previous ouputs have been presented please attempt to
                      reorder and improve them.
                      """
            request_body, headers = general_function_call(courseOutline_function, function_app_endpoint, user_prompt)
            print(f'fire for course')
            time.sleep(25)
            fire_and_forget(lambda_url, request_body, headers)
    except Exception as e:
        response = {
            'status_code': 500,
            'message': 'Internal Server Error.'
        }
    else:
        response = {
                'status_code': 200,
                'message': 'Sucess'
            }
    return response


def course_outlineChapter_prompts(request, json_data):
    #
    course_id = json_data['course_id']
    course = Course.objects.get(pk=course_id)
    nth_reflection = json_data['nth_reflection']
    module = json_data['module']
    try:
        if nth_reflection == 5 or len(course.specification.spec_content[module]['content'].keys()) > 0:
            if 'ai_response' in json_data.keys():
                chapters = json.loads(json_data['ai_response'])['chapters'].split(',')
                chapters = [s.strip() for s in chapters]
                module_content = {}
                for idd, chapter in enumerate(chapters):
                    module_content[chapter] = {
                            'active': True,
                            'content': {},
                            'questions': {},
                            'position': idd+1
                        }
                course.specification.spec_content[module]['content'] = module_content
                course.specification.save()
                nth_reflection = 0
            #
            for chapter in course.specification.spec_content[module]['content'].keys():
                courseTopicOutline_function = create_course_outline(course, item_type='topic')
                lambda_url = settings.CHATGPT_LAMBDA_URL
                function_app_endpoint = {
                        'return_url': f"{settings.SITE_URL}/AI/_function_app_endpoint",
                        'course_id': course.id,
                        'nth_reflection': 0,
                        'type': 'topic',
                        'module': module,
                        'chapter': chapter,
                        'model_name': 'gpt-3.5-turbo-0613',
                        'model_name': 'gpt-4-0613'
                    }
                user_prompt = """With the information provided for this
                          course, please continue or start creating the outline.
                          if previous ouputs have been presented please attempt to
                          expand, reorder and improve them. This outline is for the
                          provided chapter, please give a list of topics.
                          """
                request_body, headers = general_function_call(courseTopicOutline_function, function_app_endpoint, user_prompt)
                if len(course.specification.spec_content[module]['content'][chapter]['content']) == 0:
                    pass
                    #print(f'fire for {module} -> {chapter}')
                    #time.sleep(3)
                    #fire_and_forget(lambda_url, request_body, headers)
                else:
                    pass
                    #print(f'pass for {module} -> {chapter}')
                    #course_outlineTopic_prompts('', {'course_id': course.id, 'nth_reflection': 0, 'module': module, 'chapter': chapter})
            # next step
        else:
            if 'ai_response' in json_data.keys():
                chapters = json.loads(json_data['ai_response'])['chapters'].split(',')
                chapters = [s.strip() for s in chapters]
            else:
                chapters = ''
            #
            courseChapterOutline_function = create_course_outline(
                    course,
                    item_type='chapter',
                    previous_output=chapters,
                    current_module=module,
                )
            lambda_url = settings.CHATGPT_LAMBDA_URL
            function_app_endpoint = {
                    'return_url': f"{settings.SITE_URL}/AI/_function_app_endpoint",
                    'course_id': course.id,
                    'nth_reflection': nth_reflection+1,
                    'type': 'chapter',
                    'module': module,
                    'model_name': 'gpt-3.5-turbo-0613',
                    'model_name': 'gpt-4-0613'
                }
            user_prompt = """With the information provided for this
                      course, please continue or start creating the outline.
                      if previous ouputs have been presented please attempt to
                      expand, reorder and improve them. This outline is for the
                      provided module, please give a list of chapters.
                      """
            request_body, headers = general_function_call(courseChapterOutline_function, function_app_endpoint, user_prompt)
            time.sleep(25)
            print(f'fire for {module}')
            fire_and_forget(lambda_url, request_body, headers)
    except Exception as e:
        response = {
            'status_code': 500,
            'message': 'Internal Server Error.'
        }
    else:
        response = {
                'status_code': 200,
                'message': 'Sucess'
            }
    return response


def course_outlineTopic_prompts(request, json_data):
    #
    course_id = json_data['course_id']
    course = Course.objects.get(pk=course_id)
    nth_reflection = json_data['nth_reflection']
    module = json_data['module']
    chapter = json_data['chapter']
    try:
        if nth_reflection == 5 or len(course.specification.spec_content[module]['content'][chapter]['content'].keys()) > 0:
            if 'ai_response' in json_data.keys():
                topics = json.loads(json_data['ai_response'])['topics'].split(',')
                topics = [s.strip() for s in topics]
                chapter_content = {}
                for idd, topic in enumerate(topics):
                    chapter_content[topic] = {
                            'active': True,
                            'content': {},
                            'questions': {},
                            'position': idd+1
                        }
                course.specification.spec_content[module]['content'][chapter]['content'] = chapter_content
                course.specification.save()
                nth_reflection = 0
            #
            for topic in course.specification.spec_content[module]['content'][chapter]['content'].keys():
                coursePointOutline_function = create_course_outline(course, item_type='point')
                lambda_url = settings.CHATGPT_LAMBDA_URL
                function_app_endpoint = {
                        'return_url': f"{settings.SITE_URL}/AI/_function_app_endpoint",
                        'course_id': course.id,
                        'nth_reflection': 0,
                        'type': 'point',
                        'module': module,
                        'chapter': chapter,
                        'topic': topic,
                        'model_name': 'gpt-3.5-turbo-0613',
                        'model_name': 'gpt-4-0613'
                    }
                user_prompt = """With the information provided for this
                          course, please continue or start creating the outline.
                          if previous ouputs have been presented please attempt to
                          expand, reorder and improve them. This outline is for the
                          provided topic, please give a list of zettlekasten point titles.
                          """
                request_body, headers = general_function_call(coursePointOutline_function, function_app_endpoint, user_prompt)
                if len(course.specification.spec_content[module]['content'][chapter]['content']) == 0:
                    print(f'fire for {module} -> {chapter} -> {topic}')
                    time.sleep(25)
                    fire_and_forget(lambda_url, request_body, headers)
                else:
                    print(f'pass for {module} -> {chapter} -> {topic}')
                    pass
                    #course_outlinePoint_prompts('', {'course_id': course.id, 'nth_reflection': 0, 'module': module, 'chapter': chapter, 'topic': topic})
            # next step
        else:
            if 'ai_response' in json_data.keys():
                topics = json.loads(json_data['ai_response'])['topics'].split(',')
                topics = [s.strip() for s in topics]
            else:
                topics = ''
            #
            courseTopicOutline_function = create_course_outline(
                    course,
                    item_type='topic',
                    previous_output=topics,
                    current_module=module,
                    current_chapter=chapter,
                )
            lambda_url = settings.CHATGPT_LAMBDA_URL
            function_app_endpoint = {
                    'return_url': f"{settings.SITE_URL}/AI/_function_app_endpoint",
                    'course_id': course.id,
                    'nth_reflection': nth_reflection+1,
                    'type': 'topic',
                    'module': module,
                    'chapter': chapter,
                    'model_name': 'gpt-3.5-turbo-0613',
                    'model_name': 'gpt-4-0613'
                }
            user_prompt = """With the information provided for this
                      course, please continue or start creating the outline.
                      if previous ouputs have been presented please attempt to
                      reorder and improve them. This outline is for the
                      provided chapter, please give a list of topics.
                      """
            request_body, headers = general_function_call(courseTopicOutline_function, function_app_endpoint, user_prompt)
            time.sleep(25)
            print(f'fire for {module} -> {chapter}')
            fire_and_forget(lambda_url, request_body, headers)
    except Exception as e:
        response = {
            'status_code': 500,
            'message': 'Internal Server Error.'
        }
    else:
        response = {
                'status_code': 200,
                'message': 'Sucess'
            }
    return response


def lesson_prompts(request, json_data):
    lesson_part_id = json_data['part_id']
    global_order_id = json_data['global_order_id']
    local_order_id = json_data['local_order_id']
    user_prompt = json_data['user_prompt']
    ai_response = json_data['ai_response']
    ai_function_name = json_data['ai_function_name']
    unique_id = json_data['unique_id']
    #
    user_part = {"role": 'user', "content": user_prompt}
    ai_part = {"role": 'assistant', "content": ai_response}
    #
    new_stuff = [user_part, ai_part]
    if ai_function_name:
        # Your input JSON string
        ai_response_dict = json.loads(ai_response)
        ai_response_dict['unique_id'] = unique_id
        ai_response = json.dumps(ai_response_dict)
        #
        ai_function_part = {"role": 'function', "name": ai_function_name, "content": ai_response}
        new_stuff = [user_part, ai_function_part]
    try:
        lesson_part = Lesson_part.objects.get(pk=lesson_part_id)
        #
        part_chat = lesson_part.part_chat[str(int(global_order_id) - 1)]
        #
        if 'thread' in part_chat.keys():
            part_chat['thread'] = part_chat['thread'][0: int(local_order_id)*2]
            part_chat['thread'] += new_stuff
        else:
            part_chat['thread'] = new_stuff
        lesson_part.part_chat[str(int(global_order_id) - 1)] = part_chat
        lesson_part.prompt += int(0)
        lesson_part.completion += int(0)
        lesson_part.total += int(0)
        lesson_part.save()
    except Exception as e:
        response = {
                'status_code': 500,
                'message': 'Internal Server Error.'
            }
    else:
        response = {
                'status_code': 200,
                'message': 'Sucess'
            }
    return response


def course_introduction_prompts(request, json_data):
    course_id = json_data['course_id']
    ai_response = json_data['ai_response']
    #
    try:
        ai_response_dict = json.loads(ai_response)
        course = Course.objects.get(pk=course_id)
        course.course_skills = {idd: ai_response_dict['summary'][val]['skill'] for idd, val in enumerate(ai_response_dict['summary'])}
        course.course_summary = ai_response_dict['course_introduction']
        course.course_learning_objectives = {idd: ai_response_dict['summary'][val]['learning_objective'] for idd, val in enumerate(ai_response_dict['summary'])}
        course.course_publication = True
        course.save()
    except Exception as e:
        response = {
            'status_code': 500,
            'message': 'Internal Server Error.'
        }
        course = Course.objects.get(pk=course_id)
        course.course_skills = {idd: '(failed summary generation)' for idd in range(6)}
        course.course_summary = '(failed summary generation)'
        course.course_learning_objectives = {idd: '(failed summary generation)' for idd in range(6)}
        course.course_publication = False
        course.save()
    else:
        response = {
                'status_code': 200,
                'message': 'Sucess'
            }
    return response


def course_questions_prompts(request, json_data):
    q_prompt_id = json_data['q_prompt_id']
    ai_response = json_data['ai_response']
    #
    try:
        ai_response_dict = json.loads(ai_response)
        prompt_obj = ContentPromptQuestion.objects.get(pk=q_prompt_id)
        module = prompt_obj.moduel
        chapter = prompt_obj.chapter
        level = str(prompt_obj.level)
        list_questions = prompt_obj.specification.spec_content[module]['content'][chapter]['questions'][level]
        questions_objs = Question.objects.filter(q_unique_id__in=list_questions).order_by('q_number')
        for q_object, nth_q in zip(questions_objs, sorted(ai_response_dict['questions'].keys())):
            q_object.q_content = ai_response_dict['questions'][nth_q]['question']
            q_object.q_answer = ai_response_dict['questions'][nth_q]['answer'] + '\n\n' + str(ai_response_dict['questions'][nth_q]['marking_criteria'])
            q_object.q_marks = int(ai_response_dict['questions'][nth_q]['total_marks'])
            q_object.save()
        #
        questions_objs.update(author_confirmation=False)
    except Exception as e:
        print(e)
        response = {
            'status_code': 500,
            'message': 'Internal Server Error.'
        }
    else:
        response = {
                'status_code': 200,
                'message': 'Sucess'
            }
    return response


def course_point_prompts(request, json_data):
    p_prompt_id = json_data['p_prompt_id']
    ai_response = json_data['ai_response']
    #
    try:
        ai_response_dict = json.loads(ai_response)
        prompt_obj = ContentPromptPoint.objects.get(pk=p_prompt_id)
        point_unique_id = prompt_obj.p_unique
        p_object = Point.objects.get(p_unique_id=point_unique_id)
        p_object.p_content = ai_response_dict['lesson']
        p_object.author_confirmation = False
        p_object.save()
    except Exception as e:
        print(e)
        response = {
            'status_code': 500,
            'message': 'Internal Server Error.'
        }
    else:
        response = {
                'status_code': 200,
                'message': 'Sucess'
            }
    return response
