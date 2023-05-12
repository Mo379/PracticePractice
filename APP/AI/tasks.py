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
from AI.prompt import Prompter
from content.models import Course, Question
from user.models import User
from AI.models import (
        ContentGenerationJob,
        ContentPromptQuestion,
        ContentPromptTopic,
        ContentPromptPoint,
        Usage,
    )


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
course_summary and course_learning_objectives), the course_skills and \
course_learning_objectives are lists with exactly 6 entries each with each \
item in the list being a string and the summary is simply \
a string, the summary should be very informative while being short, and should\
get the student exited about the course. The values are for a course named {course_name}, has \
difficulty level of '{course_level}', and the \
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


@shared_task()
def _generate_course_content(job_id):
    prom = Prompter()
    #
    job = ContentGenerationJob.objects.get(
            pk=job_id
        )
    user = job.user
    spec = job.specification
    #
    level = spec.spec_level
    subject = spec.spec_subject
    module = job.moduel
    chapter = job.chapter
    #
    q_prmpts = ContentPromptQuestion.objects.filter(
            user=user,
            specification=spec,
            moduel=module,
            chapter=chapter,
            activated=True,
        )
    t_prmpts = ContentPromptTopic.objects.filter(
            user=user,
            specification=spec,
            moduel=module,
            chapter=chapter,
        )
    p_prmpts = ContentPromptPoint.objects.filter(
            user=user,
            specification=spec,
            moduel=module,
            chapter=chapter,
            activated=True,
        )
    #
    questions = {}
    for prompt in q_prmpts:
        text = prompt.prompt
        generated_prompt = f"Create a json response with 5 keys (1, 2, 3, 4, 5) \
where the content for each key is simply a string. \
the string for each of the keys is an exam style question, this \
is for a course staged in '{level}', where the subject is {subject}, \
the module for the questions is {module} and the chapter is {chapter}, \
the questions are of increasing difficulty and arranged in such \
a way that is easy for a beginner to build their understanding, \
overall the difficult of this list of qustions is of level {prompt.level}. \
The instructor provided the following context to help guide the style and content \
of the question, thus the question content should closely follow it with combination \
with the previous content. \n\n ('instructor_context':'{text}')."
        questions[prompt.level] = generated_prompt
    for key in sorted(list(questions.keys())):
        #response_json, response = prom.prompt('course_content_question', {}, questions[key])
        #output = json.loads(response_json)
        #q_1 = output['1']
        #q_2 = output['2']
        #q_3 = output['3']
        #q_4 = output['4']
        #q_5 = output['5']
        questions = Question.objects.filter(
                user=user,
                q_subject=subject,
                q_moduel=module,
                q_chapter=chapter,
                q_difficulty=key,
            )
        print(questions, key)
    #
    job.finished = True
    job.save()
