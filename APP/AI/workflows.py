from PP2.utils import fire_and_forget
from AI.functions import create_course_introduction
from AI.models import (
        ContentPromptQuestion,
        ContentPromptTopic,
        ContentPromptPoint,
        Lesson_quiz,
    )

#if publication_status:
#    # do course item checks
#    spec_content = course.specification.spec_content
#    active_points, active_questions = extract_active_spec_content(spec_content)
#    all_questions = Question.objects.filter(q_unique_id__in=active_questions)
#    all_points = Point.objects.filter(p_unique_id__in=active_points)
#    unconfirmed_questions = all_questions.filter(author_confirmation=False)
#    unconfirmed_points = all_points.filter(author_confirmation=False)
#    #
#    empty_content = detect_empty_content(spec_content)
#    empty_content_str = ''
#    for module in empty_content.keys():
#        empty_content_str += f'&ensp; Module: {module} <br>'
#        if len(empty_content[module])>0:
#            for chapter in empty_content[module].keys():
#                empty_content_str += f'&ensp; &ensp;Chapter: {chapter}<br>'
#                if len(empty_content[module][chapter])>0:
#                    for topic in empty_content[module][chapter].keys():
#                        empty_content_str += f"&ensp; &ensp; &ensp; Topic: {topic} <br><br>"
#    if len(empty_content) > 0:
#        messages.add_message(
#                request,
#                messages.INFO,
#                f"""
#                The following content sections are empty, please
#                add at least a single point:<br>
#                {empty_content_str}
#                """,
#                extra_tags='alert-danger course'
#            )
#        return redirect(
#                'dashboard:mycourses',
#            )
#    #
#    if len(all_questions) < 100 or len(all_points) < 20:
#        publication_status = False
#        course.course_publication = publication_status
#        course.save()
#        messages.add_message(
#                request,
#                messages.INFO,
#                f"""
#                To publish your course you need at least 100
#                questions and 20 points, currently you only have
#                {len(all_questions)} questions and
#                {len(all_points)} points, please add more content.
#                """,
#                extra_tags='alert-danger course'
#            )
#        return redirect(
#                'dashboard:mycourses',
#            )
#    #
#    if len(unconfirmed_questions) + len(unconfirmed_points) == 0:
#        publication_status = True
#        course.course_publication = publication_status
#        # Create a new course version
#        if course.course_up_to_date is not True:
#            versions = CourseVersion.objects.filter(
#                course=course
#            ).order_by(
#                    '-version_number'
#                )
#            latest_version = versions[0]
#            CourseVersion.objects.create(
#                course=course,
#                version_number=latest_version.version_number + 1,
#                version_name=version_name,
#                version_content=course.specification.spec_content,
#                version_note=version_note,
#            )
#            course.course_up_to_date = True
#        course.save()
#    else:
#        publication_status = False
#        course.course_publication = publication_status
#        course.save()
#        q_link = ""
#        p_link = ""
#        for q in unconfirmed_questions[:5]:
#            kwargs = {"spec_id": course.specification.id, "question_id": q.id}
#            url = reverse('content:editorquestion', kwargs=kwargs)
#            q_link += f"<a class='ml-2' href='{url}'>Question: {q}</a><br>"
#        for p in unconfirmed_points[:5]:
#            kwargs = {"spec_id": course.specification.id, "point_id": p.id}
#            url = reverse('content:editorpoint', kwargs=kwargs)
#            p_link += f"<a class='ml-2' href='{url}'>Point: {p}</a><br>"
#        messages.add_message(
#                request,
#                messages.INFO,
#                f"""
#                There is a total of {len(unconfirmed_questions)} and {len(unconfirmed_points)} unconfirmed questions and points,
#                please go back, check and confirm that the content is correct and free of errors, use those links to make quick confirmations: <br><br>
#                Questions:<br>{q_link}<br>
#                Points:<br>{p_link}
#                """,
#                extra_tags='alert-danger course'
#            )
#        return redirect(
#                'dashboard:mycourses',
#            )
#else:
#    course.course_publication = publication_status
#course.save()
#if regenerate_summary:
#    course.course_skills = {idd: '(AI is working...)' for idd in range(6)}
#    course.course_summary = '(AI is working...)'
#    course.course_learning_objectives = {idd: '(AI is working...)' for idd in range(6)}
#    #
#    courseIntro_function = create_course_introduction(request.user, course, 10)
#    message = {
#      "chat": [
#        {
#          "role": "system",
#          "content": courseIntro_function[2]
#        },
#        {
#          "role": "user",
#          "content": """With the information provided for this
#              course, please create a list of skills or objectives
#              that the studnet can expect to achive, do not use
#              too many words per skill or learning objective"""
#        }
#      ]
#    }
#    functions = [courseIntro_function[0]]
#    function_call = {"name": courseIntro_function[1]}
#    lambda_url = settings.CHATGPT_LAMBDA_URL
#    function_app_endpoint = {
#            'return_url': f"{settings.SITE_URL}/AI/_function_app_endpoint",
#            'course_id': course.id,
#        }
#    request_body = {
#            'message': message['chat'],
#            'functions': functions,
#            'function_call': function_call,
#            'function_app_endpoint': function_app_endpoint,
#        }
#    headers = {
#        "Content-Type": "application/json",
#    }
#    fire_and_forget(lambda_url, request_body, headers)
