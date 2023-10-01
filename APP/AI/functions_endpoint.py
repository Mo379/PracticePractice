import time
from django.conf import settings
import json
from content.util.GeneralUtil import TagGenerator
from PP2.utils import fire_and_forget
from AI.models import Lesson_part, ContentPromptQuestion, ContentPromptPoint
from AI import workflows
from AI.functions import (
    general_function_call,
    create_course_outline,
    create_course_lesson,
    create_course_questions,
    create_course_introduction,
)
from content.models import Course, Question, Point


def course_outline_prompts(request, json_data):
    #
    course_id = json_data['course_id']
    course = Course.objects.get(pk=course_id)
    nth_reflection = json_data['nth_reflection']
    #
    try:
        # see if output is valid
        if 'ai_response' in json_data.keys():
            modules = json.loads(json_data['ai_response'])['modules'].split(',')
            modules = [s.strip() for s in modules]
        print('response is valid')
    except Exception as e:
        courseOutline_function = create_course_outline(course)
        lambda_url = settings.CHATGPT_LAMBDA_URL
        function_app_endpoint = {
                'return_url': f"{settings.SITE_URL}/AI/_function_app_endpoint",
                'course_id': course.id,
                'nth_reflection': nth_reflection,
                'type': 'module',
                'model_name': 'gpt-3.5-turbo-0613',
                'model_name': 'gpt-4-0613'
            }
        user_prompt = """With the information provided for this
                  course, please continue or start creating the outline.
                  if previous ouputs have been presented please attempt to
                  reorder and improve them, please focus on generating correct json syntax.
                  """
        request_body, headers = general_function_call(courseOutline_function, function_app_endpoint, user_prompt)
        time.sleep(60)
        fire_and_forget(lambda_url, request_body, headers)
        # refire lambda if output is invalid
        response = {
            'status_code': 500,
            'message': 'Internal Server Error.'
        }
    else:
        # process response if output is valid
        if nth_reflection == 2 or len(course.specification.spec_content.keys()) > 0:
            if 'ai_response' in json_data.keys():
                modules = json.loads(json_data['ai_response'])['modules'].split(',')
                modules = [s.strip() for s in modules]
                spec_content = {}
                for idd, module in enumerate(modules):
                    spec_content[module.replace(' ', '_')] = {
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
                    time.sleep(60)
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
            time.sleep(60)
            fire_and_forget(lambda_url, request_body, headers)
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
        if 'ai_response' in json_data.keys():
            chapters = json.loads(json_data['ai_response'])['chapters'].split(',')
            chapters = [s.strip() for s in chapters]
    except Exception as e:
        courseChapterOutline_function = create_course_outline(
                course,
                item_type='chapter',
                current_module=module,
            )
        lambda_url = settings.CHATGPT_LAMBDA_URL
        function_app_endpoint = {
                'return_url': f"{settings.SITE_URL}/AI/_function_app_endpoint",
                'course_id': course.id,
                'nth_reflection': nth_reflection,
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
        print('refire chapter')
        time.sleep(60)
        (lambda_url, request_body, headers)
        response = {
            'status_code': 500,
            'message': 'Internal Server Error.'
        }
    else:
        if nth_reflection == 2 or len(course.specification.spec_content[module]['content'].keys()) > 0:
            if 'ai_response' in json_data.keys():
                chapters = json.loads(json_data['ai_response'])['chapters'].split(',')
                chapters = [s.strip() for s in chapters]
                module_content = {}
                for idd, chapter in enumerate(chapters):
                    module_content[chapter.replace(' ', '_')] = {
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
                courseTopicOutline_function = create_course_outline(course, item_type='topic', current_module=module, current_chapter=chapter)
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
                    print(f'fire for {module} -> {chapter}')
                    time.sleep(60)
                    fire_and_forget(lambda_url, request_body, headers)
                else:
                    print(f'pass for {module} -> {chapter}')
                    course_outlineTopic_prompts('', {'course_id': course.id, 'nth_reflection': 0, 'module': module, 'chapter': chapter})
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
            time.sleep(60)
            print(f'fire for {module}')
            fire_and_forget(lambda_url, request_body, headers)
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
        if 'ai_response' in json_data.keys():
            topics = json.loads(json_data['ai_response'])['topics'].split(',')
            topics = [s.strip() for s in topics]
    except Exception:
        courseTopicOutline_function = create_course_outline(course, item_type='topic', current_module=module, current_chapter=chapter)
        lambda_url = settings.CHATGPT_LAMBDA_URL
        function_app_endpoint = {
                'return_url': f"{settings.SITE_URL}/AI/_function_app_endpoint",
                'course_id': course.id,
                'nth_reflection': nth_reflection,
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
        time.sleep(60)
        fire_and_forget(lambda_url, request_body, headers)
        print('refire topic')
        response = {
            'status_code': 500,
            'message': 'Internal Server Error.'
        }
    else:
        if nth_reflection == 2 or len(course.specification.spec_content[module]['content'][chapter]['content'].keys()) > 0:
            if 'ai_response' in json_data.keys():
                topics = json.loads(json_data['ai_response'])['topics'].split(',')
                topics = [s.strip() for s in topics]
                chapter_content = {}
                for idd, topic in enumerate(topics):
                    chapter_content[topic.replace(' ', '_')] = {
                            'active': True,
                            'content': {},
                            'position': idd+1
                        }
                course.specification.spec_content[module]['content'][chapter]['content'] = chapter_content
                course.specification.save()
                nth_reflection = 0
            #
            for topic in course.specification.spec_content[module]['content'][chapter]['content'].keys():
                coursePointOutline_function = create_course_outline(
                        course,
                        item_type='point',
                        current_module=module,
                        current_chapter=chapter,
                        current_topic=topic,
                    )
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
                    time.sleep(60)
                    fire_and_forget(lambda_url, request_body, headers)
                else:
                    print(f'pass for {module} -> {chapter} -> {topic}')
                    course_outlinePoint_prompts('', {'course_id': course.id, 'nth_reflection': 0, 'module': module, 'chapter': chapter, 'topic': topic})
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
            time.sleep(60)
            print(f'fire for {module} -> {chapter} last in chain')
            fire_and_forget(lambda_url, request_body, headers)
        response = {
                'status_code': 200,
                'message': 'Sucess'
            }
    return response


def course_outlinePoint_prompts(request, json_data):
    #
    course_id = json_data['course_id']
    course = Course.objects.get(pk=course_id)
    nth_reflection = json_data['nth_reflection']
    module = json_data['module']
    chapter = json_data['chapter']
    topic = json_data['topic']
    try:
        if 'ai_response' in json_data.keys():
            points = json.loads(json_data['ai_response'])['points'].split(',')
            points = [s.strip() for s in points]
    except Exception as e:
        coursePointOutline_function = create_course_outline(
                course,
                item_type='point',
                current_module=module,
                current_chapter=chapter,
                current_topic=topic,
            )
        lambda_url = settings.CHATGPT_LAMBDA_URL
        function_app_endpoint = {
                'return_url': f"{settings.SITE_URL}/AI/_function_app_endpoint",
                'course_id': course.id,
                'nth_reflection': nth_reflection,
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
        time.sleep(60)
        fire_and_forget(lambda_url, request_body, headers)
        response = {
            'status_code': 500,
            'message': 'Internal Server Error.'
        }
    else:
        if nth_reflection == 2 or len(course.specification.spec_content[module]['content'][chapter]['content'][topic]['content'].keys()) > 0:
            if 'ai_response' in json_data.keys():
                points = json.loads(json_data['ai_response'])['points'].split(',')
                points = [s.strip() for s in points]
                topic_content = {}
                for idd, point in enumerate(points):
                    unique_id = TagGenerator()
                    Point.objects.create(
                        p_level=course.specification.spec_level,
                        p_subject=course.specification.spec_subject,
                        p_title=point,
                        p_moduel=module,
                        p_chapter=chapter,
                        p_topic=topic,
                        p_unique_id=unique_id,
                        p_number=idd,
                    )
                    topic_content[unique_id] = {
                        'active': True,
                        'position': idd+1
                    }
                course.specification.spec_content[module]['content'][chapter]['content'][topic]['content'] = topic_content
                course.specification.save()
            content = course.specification.spec_content
            failed = False
            # check if outline is complete before moving to the next step
            if len(content.keys()) == 0:
                failed = True
            for module in content.keys():
                if len(content[module]['content'].keys()) == 0:
                    failed = True
                for chapter in content[module]['content'].keys():
                    if len(content[module]['content'][chapter]['content'].keys()) == 0:
                        failed = True
                    for topic in content[module]['content'][chapter]['content'].keys():
                        if len(content[module]['content'][chapter]['content'][topic]['content'].keys()) == 0:
                            failed = True
            if failed == False:
                course.generated_outline = True
                course.save()
                print('running content generation')
                workflows._generated_content(course)
                #
            #
        else:
            if 'ai_response' in json_data.keys():
                points = json.loads(json_data['ai_response'])['points'].split(',')
                points = [s.strip() for s in points]
            else:
                points = ''
            print('points generated: ', points)
            #
            coursePointOutline_function = create_course_outline(
                    course,
                    item_type='point',
                    previous_output=points,
                    current_module=module,
                    current_chapter=chapter,
                    current_topic=topic,
                )
            lambda_url = settings.CHATGPT_LAMBDA_URL
            function_app_endpoint = {
                    'return_url': f"{settings.SITE_URL}/AI/_function_app_endpoint",
                    'course_id': course.id,
                    'nth_reflection': nth_reflection+1,
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
                      reorder and improve them. This outline is for the
                      provided points, please give a list of point titles (less than 6 words.), remember
                      a point is like a zettlekasten idea or is the smallest unit in the course
                      it gives the user the fundemental idea and the collection of points
                      in the topic are all related and result in a more complicated idea being formed
                      this is very important to encode into the points you're about to write.
                      """
            request_body, headers = general_function_call(coursePointOutline_function, function_app_endpoint, user_prompt)
            time.sleep(60)
            print(f'fire for {module} -> {chapter} -> {topic}')
            fire_and_forget(lambda_url, request_body, headers)
        response = {
                'status_code': 200,
                'message': 'Sucess'
            }
    return response


def course_point_prompts(request, json_data):
    course_id = json_data['course_id']
    point_id = json_data['point_id']
    ai_response = json_data['ai_response']
    #
    course = Course.objects.get(pk=course_id)
    p_object = Point.objects.get(pk=point_id)
    #
    try:
        ai_response_dict = json.loads(ai_response, strict=False)
    except Exception as e:
        print(ai_response)
        print(e)
        courseLesson_function = create_course_lesson('', course, p_object)
        lambda_url = settings.CHATGPT_LAMBDA_URL
        function_app_endpoint = {
                'return_url': f"{settings.SITE_URL}/AI/_function_app_endpoint",
                'course_id': course.id,
                'point_id': p_object.id,
                'model_name': 'gpt-3.5-turbo-0613',
                'model_name': 'gpt-4-0613'
            }
        user_prompt = """With the information provided for this
                  course, please write the lesson following the lesson prompt generated in the function.
                  please also make sure to escape any special characters, such that my python code can 
                  interpret the json correctly.
                  """
        request_body, headers = general_function_call(courseLesson_function, function_app_endpoint, user_prompt)
        #time.sleep(60)
        #fire_and_forget(lambda_url, request_body, headers)
        response = {
            'status_code': 500,
            'message': 'Internal Server Error.'
        }
    else:
        p_object.p_content = ai_response_dict['lesson']
        p_object.author_confirmation = False
        p_object.save()
        content = course.specification.spec_content
        # check if outline is complete before moving to the next step
        all_points = []
        for module in content.keys():
            for chapter in content[module]['content'].keys():
                for topic in content[module]['content'][chapter]['content'].keys():
                    for point in content[module]['content'][chapter]['content'][topic]['content'].keys():
                        all_points.append(point)
        empty_points = Point.objects.filter(p_unique_id__in=all_points, p_content={})
        if len(empty_points) == 0:
            course.generated_content = True
            course.save()
            workflows._generated_questions(course)
        response = {
                'status_code': 200,
                'message': 'Sucess'
            }
    return response


def course_questions_prompts(request, json_data):
    course_id = json_data['course_id']
    module = json_data['module']
    chapter = json_data['chapter']
    level = json_data['level']
    ai_response = json_data['ai_response']
    #
    course = Course.objects.get(pk=course_id)
    try:
        ai_response_dict = json.loads(ai_response, strict=False)
    except Exception as e:
        courseQuestions_function = create_course_questions(course, module, chapter, level)
        lambda_url = settings.CHATGPT_LAMBDA_URL
        function_app_endpoint = {
                'return_url': f"{settings.SITE_URL}/AI/_function_app_endpoint",
                'course_id': course.id,
                'module': module,
                'chapter': chapter,
                'level': level,
                'model_name': 'gpt-3.5-turbo-0613',
                'model_name': 'gpt-4-0613'
            }
        user_prompt = """With the information provided for this
                  course, please write questions following the specification and details provided.
                  """
        request_body, headers = general_function_call(courseQuestions_function, function_app_endpoint, user_prompt)
        time.sleep(60)
        fire_and_forget(lambda_url, request_body, headers)
        response = {
            'status_code': 500,
            'message': 'Internal Server Error.'
        }
    else:
        course = Course.objects.get(pk=course_id)
        list_questions = course.specification.spec_content[module]['content'][chapter]['questions'][level]
        questions_objs = Question.objects.filter(q_unique_id__in=list_questions).order_by('q_number')
        for q_object, nth_q in zip(questions_objs, sorted(ai_response_dict['questions'].keys())):
            q_object.q_content = ai_response_dict['questions'][nth_q]['question']
            q_object.q_answer = ai_response_dict['questions'][nth_q]['answer'] + '\n\n' + str(ai_response_dict['questions'][nth_q]['marking_criteria'])
            q_object.q_marks = int(ai_response_dict['questions'][nth_q]['total_marks'])
            q_object.save()
        #
        questions_objs.update(author_confirmation=False)
        #
        content = course.specification.spec_content
        all_generated = True
        for module in content.keys():
            for chapter in content[module]['content'].keys():
                questions = content[module]['content'][chapter]['questions']
                for level in questions.keys():
                    level_questions = Question.objects.filter(q_unique_id__in=questions[level])
                    q_content_fail = False
                    for question_obj in level_questions:
                        if len(question_obj.q_content) == 0:
                            q_content_fail = True
                        print(question_obj.q_content)
                    if q_content_fail:
                        all_generated = False
        if all_generated:
            course.generated_questions = True
            course.save()
            workflows._generated_summary(course)
        response = {
                'status_code': 200,
                'message': 'Sucess'
            }
    return response


def course_introduction_prompts(request, json_data):
    course_id = json_data['course_id']
    ai_response = json_data['ai_response']
    #
    course = Course.objects.get(pk=course_id)
    try:
        ai_response_dict = json.loads(ai_response, strict=False)
    except Exception as e:
        courseSummary_function = create_course_introduction(course)
        lambda_url = settings.CHATGPT_LAMBDA_URL
        function_app_endpoint = {
                'return_url': f"{settings.SITE_URL}/AI/_function_app_endpoint",
                'course_id': course.id,
                'model_name': 'gpt-3.5-turbo-0613',
                'model_name': 'gpt-4-0613'
            }
        user_prompt = """With the information provided for this
                  course, please write the course introduction summary and etc.
                  """
        request_body, headers = general_function_call(courseSummary_function, function_app_endpoint, user_prompt)
        time.sleep(60)
        fire_and_forget(lambda_url, request_body, headers)
        response = {
            'status_code': 500,
            'message': 'Internal Server Error.'
        }
    else:
        course = Course.objects.get(pk=course_id)
        course.course_skills = {idd: ai_response_dict['summary'][val]['skill'] for idd, val in enumerate(ai_response_dict['summary'])}
        course.course_summary = ai_response_dict['course_introduction']
        course.course_learning_objectives = {idd: ai_response_dict['summary'][val]['learning_objective'] for idd, val in enumerate(ai_response_dict['summary'])}
        course.course_publication = True
        course.save()
        workflows._launch_new_version(course)
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
