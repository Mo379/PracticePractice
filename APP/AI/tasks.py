import os
import time
import collections
from celery import shared_task
from django.core.mail import send_mail
from content.util.GeneralUtil import (
        order_full_spec_content,
        order_live_spec_content
    )
import json
from AI.models import Usage
from AI.prompt import Prompter
from content.models import Course
from user.models import User


@shared_task()
def _generate_course_introductions(user_id, course_id):
    prom = Prompter()
    #
    user = User.objects.get(pk=user_id)
    course = Course.objects.get(pk=course_id)
    content = course.specification
    content = order_live_spec_content(content.spec_content)
    modules = list(content.keys())
    mod_chap = collections.OrderedDict({})
    for module in modules:
        _chapters = list(content[module]['content'].keys())
        mod_chap[module] = _chapters
    context = "Course_chapters{"
    for module in mod_chap.keys():
        chapters = mod_chap[module]
        for chapter in chapters:
            context += f'{chapter}\n'
    context += "}"
    # Prompt context generation
    course_name = course.course_name
    course_level = course.course_level
    course_spec_level = course.specification.spec_level
    course_spec_subject = course.specification.spec_subject
    prompt = f"Create a json response with 3 keys (course_skills, \
course_summary and course_learning_objectives), the skills and \
summary are lists with exactly 6 entries each and the summary is simply \
a string, the summary should be very informative while being short, and shoud \
get the student exited about the course. The values are for a course named {course_name}, has \
difficulty level of '{course_level}-{course_spec_level}', and the \
course subject is {course_spec_subject}. Use the following chapters list \
to create an informative summary \n\n{context}"
    #
    response_json, response = prom.prompt('course_introductions', {}, prompt)
    output = json.loads(response_json)
    #
    tok_model = response['model']
    tok_prompt = response['usage']['prompt_tokens']
    tok_completion = response['usage']['completion_tokens']
    tok_total = response['usage']['total_tokens']
    #
    Usage.objects.create(
            user=user,
            model=tok_model,
            prompt=tok_prompt,
            completion=tok_completion,
            total=tok_total,
        )
    #
    course.course_skills = {idd: val for idd, val in enumerate(output['course_skills'])}
    course.course_summary = output['course_summary']
    course.course_learning_objectives = {idd: val for idd, val in enumerate(output['course_learning_objectives'])}
    course.course_publication = True
    #
    course.save()
