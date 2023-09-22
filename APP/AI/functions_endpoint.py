import json
from AI.models import Lesson_part, ContentPromptQuestion, ContentPromptPoint
from content.models import Course, Question, Point


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
        p_object.p_content = ai_response_dict['point']
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
