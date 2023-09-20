import json
from AI.models import Lesson_part
from content.models import Course


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
        print(ai_response_dict)
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
