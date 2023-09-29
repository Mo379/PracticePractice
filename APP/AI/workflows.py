import time
import threading
from django.conf import settings
from content.util.GeneralUtil import ChapterQuestionGenerator
from PP2.utils import fire_and_forget
from content.models import Point
from AI.functions import (
        general_function_call,
        create_course_introduction,
        create_course_outline,
        create_course_lesson,
        create_course_questions
    )
from AI.functions_endpoint import (course_outline_prompts)
from AI.models import (
        ContentPromptQuestion,
        ContentPromptTopic,
        ContentPromptPoint,
        Lesson_quiz,
    )
from content.models import Question, Course, CourseVersion


def _generate_outline(course):
    if course.generated_outline is False:
        courseOutline_function = create_course_outline(course)
        lambda_url = settings.CHATGPT_LAMBDA_URL
        function_app_endpoint = {
                'return_url': f"{settings.SITE_URL}/AI/_function_app_endpoint",
                'course_id': course.id,
                'nth_reflection': 0,
                'type': 'module',
                'model_name': 'gpt-3.5-turbo-0613',
                #'model_name': 'gpt-4-0613'
            }
        user_prompt = """With the information provided for this
                  course, please continue or start creating the outline.
                  if previous ouputs have been presented please attempt to
                  reorder and improve them.
                  """
        request_body, headers = general_function_call(courseOutline_function, function_app_endpoint, user_prompt)
        if course.course_type == 'Course':
            if len(course.specification.spec_content) == 0:
                mini_course = {
                        course.course_name.replace(' ', '_'): {
                            'active': True,
                            'content': {},
                            'position': 1
                        }
                    }
                course.specification.spec_content = mini_course
                course.specification.save()
        elif course.course_type == 'Article':
            if len(course.specification.spec_content) == 0:
                mini_course = {
                        course.course_name.replace(' ', '_'): {
                            'active': True,
                            'content': {
                                    f"module_{course.course_name.replace(' ', '_')}": {
                                        'active': True,
                                        'content': {
                                            },
                                        'position': 1,
                                        'questions': {}
                                    }
                                },
                            'position': 1
                        }
                    }
                course.specification.spec_content = mini_course
                course.specification.save()
        if len(course.specification.spec_content) == 0:
            fire_and_forget(lambda_url, request_body, headers)
        else:
            threading.Thread(
                target=course_outline_prompts,
                args=(
                    '', {'course_id': course.id, 'nth_reflection': 0}
                )
            ).start()
    else:
        threading.Thread(
            target=_generated_content,
            args=(course,)
        ).start()


def _generated_content(course):
    if course.generated_content is False:
        content = course.specification.spec_content
        for module in content.keys():
            for chapter in content[module]['content'].keys():
                for topic in content[module]['content'][chapter]['content'].keys():
                    for point in content[module]['content'][chapter]['content'][topic]['content'].keys():
                        point_obj = Point.objects.get(p_unique_id=point)
                        if len(point_obj.p_content) == 0:
                            courseLesson_function = create_course_lesson('', course, point_obj)
                            lambda_url = settings.CHATGPT_LAMBDA_URL
                            function_app_endpoint = {
                                    'return_url': f"{settings.SITE_URL}/AI/_function_app_endpoint",
                                    'course_id': course.id,
                                    'point_id': point_obj.id,
                                    'model_name': 'gpt-3.5-turbo-0613',
                                    #'model_name': 'gpt-4-0613'
                                }
                            user_prompt = """With the information provided for this
                                      course, please write the lesson following the lesson prompt generated in the function.
                                      """
                            request_body, headers = general_function_call(courseLesson_function, function_app_endpoint, user_prompt)
                            print(f'fire for point: {point}')
                            fire_and_forget(lambda_url, request_body, headers)
                            #time.sleep(60)
                        else:
                            print(f'pass for point: {point}')
    else:
        _generated_questions(course)


def _generated_questions(course):
    if course.generated_questions is False:
        subject = course.specification.spec_subject
        content = course.specification.spec_content
        for module in content.keys():
            module_content = content[module]['content']
            module_content = ChapterQuestionGenerator(subject, module, module_content)
            course.specification.spec_content[module]['content'] = module_content
            course.specification.save()
        all_generated = True
        for module in content.keys():
            for chapter in content[module]['content'].keys():
                questions = content[module]['content'][chapter]['questions']
                for level in questions.keys():
                    courseQuestions_function = create_course_questions(course, module, chapter, level)
                    lambda_url = settings.CHATGPT_LAMBDA_URL
                    function_app_endpoint = {
                            'return_url': f"{settings.SITE_URL}/AI/_function_app_endpoint",
                            'course_id': course.id,
                            'module': module,
                            'chapter': chapter,
                            'level': level,
                            'model_name': 'gpt-3.5-turbo-0613',
                            #'model_name': 'gpt-4-0613'
                        }
                    user_prompt = """With the information provided for this
                              course, please write questions following the specification and details provided.
                              """
                    request_body, headers = general_function_call(courseQuestions_function, function_app_endpoint, user_prompt)
                    level_questions = Question.objects.filter(q_unique_id__in=questions[level])
                    q_content_fail = False
                    for question_obj in level_questions:
                        if len(question_obj.q_content) == 0:
                            q_content_fail = True
                        print(question_obj.q_content)
                    if q_content_fail:
                        print(f'fire for level: {level}')
                        fire_and_forget(lambda_url, request_body, headers)
                        all_generated = False
                        #time.sleep(60)
        if all_generated:
            course.generated_questions = True
            course.save()
            _generated_summary(course)
    else:
        _generated_summary(course)


def _generated_summary(course):
    if course.generated_summary is False:
        courseSummary_function = create_course_introduction(course)
        lambda_url = settings.CHATGPT_LAMBDA_URL
        function_app_endpoint = {
                'return_url': f"{settings.SITE_URL}/AI/_function_app_endpoint",
                'course_id': course.id,
                'model_name': 'gpt-3.5-turbo-0613',
                #'model_name': 'gpt-4-0613'
            }
        user_prompt = """With the information provided for this
                  course, please write the course introduction summary and etc.
                  """
        request_body, headers = general_function_call(courseSummary_function, function_app_endpoint, user_prompt)
        if len(course.course_learning_objectives) == 0:
            fire_and_forget(lambda_url, request_body, headers)
        else:
            course.generated_summary = True
            course.course_publication = True
            course.save()
            _launch_new_version(course)
    else:
        course.course_publication = True
        course.save()
        _launch_new_version(course)


def _launch_new_version(course):
    from content.util.GeneralUtil import TagGenerator
    versions = CourseVersion.objects.filter(
        course=course
    ).order_by(
            '-version_number'
        )
    latest_version = versions[0]
    random_version_info = TagGenerator()
    CourseVersion.objects.create(
        course=course,
        version_number=latest_version.version_number + 1,
        version_name=random_version_info,
        version_content=course.specification.spec_content,
        version_note=random_version_info,
    )
