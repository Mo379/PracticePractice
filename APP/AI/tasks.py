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
from AI import prompts
from content.models import Course, Question, Point
from user.models import User
from AI.models import (
        ContentGenerationJob,
        ContentPromptQuestion,
        ContentPromptTopic,
        ContentPromptPoint,
        Usage,
    )
import asyncio
from asgiref.sync import sync_to_async



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
    course_spec_subject = course.specification.spec_subject
    #
    prompt = prompts.course_introduction_prompt(
            course_name, course_level, course_spec_subject, context
        )
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
    questions_prompts = {}
    points_prompts = {}
    for prompt in q_prmpts:
        text = prompt.prompt
        generated_prompt = prompts.questions_prompt(
                level, subject, module, chapter, prompt.level, text
                )
        questions_prompts[prompt.level] = generated_prompt
    for prompt in p_prmpts:
        topic = prompt.topic
        topic_text = t_prmpts.filter(topic=topic)[0].prompt
        point_text = prompt.prompt
        point = Point.objects.get(p_unique_id=prompt.p_unique)
        point_title = point.p_title
        generated_prompt = prompts.points_prompt(
                level, subject, module, chapter, point_title, topic_text, point_text
            )
        points_prompts[prompt.p_unique] = generated_prompt

    async def _get_answers(answer_prompts, spec):
        job_list = []
        for key in sorted(list(answer_prompts.keys())):
            job_list.append(
                asyncio.create_task(
                    prom.async_prompt(
                        'course_content_answer',
                        {},
                        answer_prompts[key],
                    )
                )
            )
        responses = await asyncio.gather(*job_list)
        for key, response in zip(sorted(list(answer_prompts.keys())), responses):
            response_content = response['choices'][0]['message']['content']
            #
            q = await sync_to_async(Question.objects.get)(pk=key)
            q.q_answer = response_content
            q.author_confirmation = False
            await sync_to_async(q.save)()
        return responses

    async def _get_questions(questions_prompts, spec):
        job_list = []
        for key in sorted(list(questions_prompts.keys())):
            job_list.append(
                asyncio.create_task(
                    prom.async_prompt(
                        'course_content_question',
                        {},
                        questions_prompts[key],
                    )
                )
            )
        responses = await asyncio.gather(*job_list)
        for key, response in zip(sorted(list(questions_prompts.keys())), responses):
            response_content = response['choices'][0]['message']['content']
            output = json.loads(response_content)
            #
            _questions = spec.spec_content[module]['content'][chapter]['questions'][str(key)]
            for question, out in zip(_questions, output):
                q = await sync_to_async(Question.objects.get)(q_unique_id=question)
                q.q_content = output[out]
                q.author_confirmation = False
                await sync_to_async(q.save)()
        return responses
    async def _get_points(points_prompts, spec):
        job_list = []
        for key in sorted(list(points_prompts.keys())):
            job_list.append(
                asyncio.create_task(
                    prom.async_prompt(
                        'course_content_point',
                        {},
                        points_prompts[key],
                    )
                )
            )
        responses = await asyncio.gather(*job_list)
        for key, response in zip(sorted(list(points_prompts.keys())), responses):
            response_content = response['choices'][0]['message']['content']
            output = json.loads(response_content)
            #
            full_result = {}
            for idd, out in enumerate(output):
                result = output[out]
                full_result[str(idd)] = {'text': str(result)}
            p = await sync_to_async(Point.objects.get)(p_unique_id=key)
            p.p_content = full_result
            p.author_confirmation = False
            await sync_to_async(p.save)()
        return responses
    #
    q_responses = asyncio.run(_get_questions(questions_prompts, spec))
    p_responses = asyncio.run(_get_points(points_prompts, spec))
    answer_prompts = {}
    for key, response in zip(sorted(list(questions_prompts.keys())), q_responses):
        _questions = spec.spec_content[module]['content'][chapter]['questions'][str(key)]
        for question in _questions:
            q = Question.objects.get(q_unique_id=question)
            text = q.q_content
            generated_prompt = prompts.answers_prompt(
                    level, subject, module, chapter, text
                    )
            answer_prompts[q.id] = generated_prompt
    a_responses = asyncio.run(_get_answers(answer_prompts, spec))
    #
    job.model = prom.model
    for q_resp in q_responses:
        toks_prompt = q_resp['usage']['prompt_tokens']
        toks_completion = q_resp['usage']['completion_tokens']
        toks_total = q_resp['usage']['total_tokens']
        #
        job.prompt += int(toks_prompt)
        job.completion += int(toks_completion)
        job.total += int(toks_total)
    for p_resp in p_responses:
        toks_prompt = p_resp['usage']['prompt_tokens']
        toks_completion = p_resp['usage']['completion_tokens']
        toks_total = p_resp['usage']['total_tokens']
        #
        job.prompt += int(toks_prompt)
        job.completion += int(toks_completion)
        job.total += int(toks_total)
    for a_resp in a_responses:
        toks_prompt = a_resp['usage']['prompt_tokens']
        toks_completion = a_resp['usage']['completion_tokens']
        toks_total = a_resp['usage']['total_tokens']
        #
        job.prompt += int(toks_prompt)
        job.completion += int(toks_completion)
        job.total += int(toks_total)
    #
    q_prmpts.update(activated=False)
    p_prmpts.update(activated=False)
    #
    job.finished = True
    job.save()
