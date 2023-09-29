<<<<<<< HEAD
=======
from django.conf import settings
>>>>>>> develop
import re
import collections
from content.util.GeneralUtil import (
        order_full_spec_content,
        order_live_spec_content
    )
from AI.models import ContentPromptTopic
from content.models import Course, Question, Point
from user.models import User


personality_prompt = """

"""
md_mj_formatting_prompt = """

"""
keyword_formatting_prompt = """
<<<<<<< HEAD

"""

def create_course_lesson(request, instructor_context, point_prompt_obj):
    spec = point_prompt_obj.specification
    level = spec.spec_level
    subject = spec.spec_subject
    module = point_prompt_obj.moduel
    topic = point_prompt_obj.topic
    chapter = point_prompt_obj.chapter
    t_prmpts = ContentPromptTopic.objects.filter(
            user=request.user,
            specification=spec,
            moduel=module,
            chapter=chapter,
        )
    topic_text = t_prmpts.filter(topic=topic)[0].prompt
    point_text = point_prompt_obj.prompt
    point = Point.objects.get(p_unique_id=point_prompt_obj.p_unique)
    point_title = point.p_title
    def points_prompt(level, subject, module, chapter, point_title, topic_text, point_text, instructor_context):
        return re.sub('\s+', ' ', f"You are a very good teacher that understands the importance of \
                creating good lessons, and are tasked with writing text book course content for a course \
                The course is staged in '{level}', where the subject is {subject}, \
            the module for content is {module} and the chapter is {chapter}, \
            create a short lesson for the lesson point titled '{point_title}', that \
            teaches this in a way that is easy \
            to build an understanding and gets straight to the point without much of an introduction, use the following \
            context to help with the content of the lesson, \
            [ {topic_text} ] [{point_text} ]'). For formatting \
            you must only use only text and mathjax latex notation ($ for inline maths and $$ for bloack maths), \
            dont user any character that invalidates reading the json output, \
            The lesson shold be informative and easy to understand and not too long (make it the right length to get the idea across). \
            instructor context : {instructor_context}.")
    system_message = points_prompt(level, subject, module, chapter, point_title, topic_text, point_text, instructor_context)
    function_description = {
        "name": "create_course_lesson",
        "description": "Creates a lesson for the content or topic description provided using mathjax and only text",
        "parameters": {
            "type": "object",
            "properties": {
                "lesson": {
                    "type": "string",
                    "description": "The lesson being taught, this should be a detailed and understandable lesson.",
                },
            },
            "required": [
                "lesson"
            ],
        },
    }
    return function_description, 'create_course_lesson', system_message
=======
wrap any keyword used with (<span class='keyword'>)
"""


def general_function_call(function_output, function_app_endpoint, user_prompt):
    message = {
      "chat": [
        {
          "role": "system",
          "content": function_output[2]
        },
        {
          "role": "user",
          "content": re.sub('\s+', ' ', user_prompt)
        }
      ]
    }
    functions = [function_output[0]]
    function_call = {"name": function_output[1]}
    request_body = {
            'message': message['chat'],
            'functions': functions,
            'function_call': function_call,
            'function_app_endpoint': function_app_endpoint,
        }
    headers = {
        "Content-Type": "application/json",
    }
    return request_body, headers
def create_course_outline(
        course,
        previous_output='',
        item_type='module',
        current_module='',
        current_chapter='',
        current_topic=''
        ):
    generated_modules = 'This course is new and no modules have been generated yet'
    generated_chapters = ''
    generated_topics = ''
    generated_modules = ''
    #
    if item_type in ['chapter', 'topic', 'point']:
        generated_modules = f"""
            The following are the modules already in the course, only use them as guidance:
            {course.specification.spec_content.keys()}
        """
    if item_type in ['topic', 'point']:
        generated_chapters = course.specification.spec_content[current_module]['content'].keys()
        generated_chapters = f"""
            The following are the chapters already in the course, only use them as guidance:
            {generated_chapters}
        """
    if item_type in ['point']:
        generated_topics = course.specification.spec_content[current_module]['content'][current_chapter]['content'].keys()
        generated_topics = f"""
            The following are the topics already in the course, only use them as guidence:
            {generated_topics}
        """
    if current_module:
        current_module = f"The current module is {current_module}"
    if current_chapter:
        current_chapter = f", the current chapter is {current_chapter}"
    if current_topic:
        current_topic = f", the current topic is {current_topic}"
    #
    #
    course_name = course.course_name
    course_level = course.course_level
    course_spec_level = course.specification.spec_level
    course_spec_subject = course.specification.spec_subject
    course_description = course.course_description
    def outline_prompt(
            course_name,
            course_level,
            course_spec_level,
            course_spec_subject,
            course_description,
            item_type,
            current_module=current_module,
            current_chapter=current_chapter,
            current_topic=current_topic,
            #
            generated_modules=generated_modules,
            generated_chapters=generated_chapters,
            generated_topics=generated_topics,
            ):
        prompt = f"""
        You're an expert tutor with good knowledge of many fields.
        This outline should fully describe a small and easy to consume course.
        The overall structure follows this schema/scope structure (module:chapter:topic:point),
        where the module is the higest abstraction of the course outline, followed
        by the chapter then topic and finally point (a point is like a zettlekasten idea [this is important]).
        Your job is to create the small and easy to consume outline that gives the student a good
        amount of knowledge (the essentials), where you're only
        generating one of the provided four options, in this case, only write ({item_type}s)
        and closely follow the function and its provided description.
        You must also pay close attention to the following as it will guide you.
        Make the outline comprehensive and avoid missing any important/critical items
        and dont forget to make the course short.
        try to seperate the content as much as possible so that each {item_type} is completely independent of others.

        The following is the general information for this course:
        course name: {course_name},
        course difficulty: {course_level},
        course target: {course_spec_level},
        course subject: {course_spec_subject},
        course description: {course_description},

        {generated_modules}
        {generated_chapters}
        {generated_topics}
        {current_module}
        {current_chapter}
        {current_topic}

        course {item_type} previous outline: {previous_output},

        Be sure to strip out things like '{item_type} 1:' from the lists, this is not
        required, and ensure that the list provided is comma seprable, and remove any
        repeating or very similar {item_type} from the outline without hesistation.
        You're free to remove any item from the previous outline if you think it's not constructive
        for learning this topic.
        pay close attention to which current module, chapter and topic you're writing for.
        And rememeber to make the course comprehensive short and welcoming to the specified
        target and difficulty, so do not include anything that is unnessary.
        Ensure that the number of {item_type} is not too long as this may discourage the learners/students and we dont want that.
        This is so that the course is not too long, so ensure that the {item_type} cover only the very very key concepts.
        Be sure to not repeat anything that is previously present or could be present in the already generated modules chapters or topics.
        """
        return re.sub('\s+', ' ', prompt)
    #
    system_message = outline_prompt(course_name, course_level, course_spec_level, course_spec_subject, course_description, item_type)
    function_description = {
        "name": "create_course_outline",
        "description": "Create or improve an outline for the course described, the current scope is for {item_type}s so only {item_type}s will be created.",
        "parameters": {
            "type": "object",
            "properties": {
                f"{item_type}s": {
                    "type": "string",
                    "description": f"A comma sepearted unordered list of {item_type}s",
                },
            },
            "required": [
                f"{item_type}s"
            ],
        },
    }
    return function_description, 'create_course_outline', system_message
>>>>>>> develop


def create_course_lesson(request, course, point):
    spec = course.specification
    level = spec.spec_level
    subject = spec.spec_subject
    module = point.p_moduel
    topic = point.p_topic
    chapter = point.p_chapter
    point_title = point.p_title
    def points_prompt(level, subject, module, chapter, topic, point_title):
        return re.sub('\s+', ' ', f"You are a very good teacher that understands the importance of \
                creating good lessons, and are tasked with writing text book course content for a course \
                The course is staged in '{level}', where the subject is {subject}, \
            the module for content is {module} ,the chapter is {chapter} and the topic is {topic}, \
            create a short lesson for the lesson point titled '{point_title}', that \
            teaches this in a way that is easy \
            to build an understanding and gets straight to the point without much of an introduction. For formatting \
            you must only use only text and mathjax latex notation ($ for inline maths and $$ for bloack maths), \
            dont user any character that invalidates reading the json output, \
            The lesson shold be informative and easy to understand and not too long (make it the right length to get the idea across). \
            Here you are generating something akin to a zettlekasten idea, and making the explanation/examples really easy to understand. \
            use the lesson prompt as guidance to write the lesson field.")
    system_message = points_prompt(level, subject, module, chapter, topic, point_title)
    function_description = {
        "name": "create_course_lesson",
        "description": "Creates a lesson for the content or topic description provided using mathjax and only text",
        "parameters": {
            "type": "object",
            "properties": {
                "Lesson_prompt": {
                    "type": "string",
                    "description": "A prompt that tells chatgpt how to design this lesson appropriately and what exactly needs to be added.",
                },
                "lesson": {
                    "type": "string",
                    "description": "The lesson being taught, this should be a detailed and understandable lesson.",
                },
            },
            "required": [
                "Lesson_prompt", "lesson"
            ],
        },
    }
    return function_description, 'create_course_lesson', system_message


def create_course_questions(course, module, chapter, level, n_questions=5):
    #
    spec = course.specification
    #
    level = spec.spec_level
    subject = spec.spec_subject
    def questions_prompt(level, subject, module, chapter, prompt_level):
        return f"This is for a course staged in '{level}', where the subject is {subject}, \
            the module for the questions is {module} and the chapter is {chapter}, \
            the questions are of increasing difficulty and arranged in such \
            a way that is easy for a beginner to build their understanding, \
            overall the difficult of this list of qustions is of level {prompt_level} out of 5 levels\
            so please estimate and adjust for the difficulty. \
            The instructor provided the following context to help guide the style and content \
            of the question, thus the question content should closely follow it with combination \
            with the previous context."
    #
    system_message = questions_prompt(level, subject, module, chapter, level)
    function_outline = [
        {
            "type": 'object',
            'properties': {
                "question": {
                    "type": "string",
                    "description": f"Question {id+1}. (using mathjax $ maths)",
                },
                "answer": {
                    "type": 'string',
                    "description": f"A detailed step by step answer to question {id+1}, this is an explanation of the resoning behind the solution. (using mathjax $ maths and showing the number of marks behind each step)",
                },
                "marking_criteria": {
                    "type": 'string',
                    "description": f"And explanation for where in the method or for what reason each mark should be given for question {id+1}",
                },
                "total_marks": {
                    "type": 'string',
                    "description": f"An intiger stating the number of marks for question {id+1}.",
                },
            }
        }
        for id in range(n_questions)
    ]
    function_description = {
        "name": "create_course_questions",
        "description": "Create questions for the content or topic provided",
        "parameters": {
            "type": "object",
            "properties": {
                "chatgpt_questions_prompt": {
                    "type": 'string',
                    "description": f"A prompt for chat gpt to use to be able to generate better quality questions.",
                },
            },
            "required": [
                "chatgpt_questions_prompt", "questions"
            ],
        },
    }
    function_description['parameters']['properties']['questions'] = {}
    function_description['parameters']['properties']['questions']['type'] = "object"
    function_description['parameters']['properties']['questions']['properties'] = {}
    function_description['parameters']['properties']['questions']['description'] = "The questions requested is outlined in this value, it contains the questions, answers and marks."
    for idd, question_dict in enumerate(function_outline):
        idd += 1
        function_description['parameters']['properties']['questions']['properties'][idd] = question_dict
    return function_description, 'create_course_questions', system_message


def create_course_introduction(course, n_skills=10):
    content = course.specification
    content = order_live_spec_content(content.spec_content)
    modules = list(content.keys())
    mod_chap = collections.OrderedDict({})
    for module in modules:
        _chapters = list(content[module]['content'].keys())[0:3]
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
    def course_introduction_prompt(course_name, course_level, course_spec_subject, context):
        return f"""Please only use the provided information to generate the course introduction,
            learning objectives and skills, get the student exited about the
            course. The values are for a course named {course_name}, it has
        difficulty level of '{course_level}', and the
        course subject is {course_spec_subject}. The course summary is a paragraph long, and the objectives
        are short and skills are a single or two words. Use the following chapters list
        to create an informative summary \n\n{context}."""
    #
    system_message = course_introduction_prompt(
            course_name, course_level, course_spec_subject, context
        )
    function_outline = [
        {
            "type": 'object',
            'properties': {
                "learning_objective": {
                    "type": "string",
                    "description": f"Learning objective {id + 1}.",
                },
                "skill": {
                    "type": "string",
                    "description": f"Skill {id+1}.",
                },
            }
        }
        for id in range(n_skills)
    ]
    function_description = {
        "name": "create_course_introduction",
        "description": "Create a list of skills that the student gains from the provided content.",
        "parameters": {
            "type": "object",
            "properties": {
                "course_introduction": {
                    "type": "string",
                    "description": """A detailed course introduction, this 
                    should be slightly longer than a paragraph, and sholuld
                    get the students exited about the course, mention the
                    course's level and some of the best chapters here.""",
                },
            },
            "required": [
                "course_introduction","summary"
            ],
        },
    }
    function_description['parameters']['properties']['summary'] = {}
    function_description['parameters']['properties']['summary']['type'] = "object"
    function_description['parameters']['properties']['summary']['properties'] = {}
    function_description['parameters']['properties']['summary']['description'] = "The list of learning objectives and skills that the course provides for the students."
    for idd, items_dict in enumerate(function_outline):
        idd += 1
        function_description['parameters']['properties']['summary']['properties'][idd] = items_dict
    return function_description, 'create_course_introduction', system_message


def create_quiz_function(n_questions=5):
    function_outline = [
        {
            "type": 'object',
            'properties':{
                "question": {
                    "type": "string",
                    "description": f"Question {id+1} in the multiple choice quiz. (using mathjax $ maths)",
                },
                "choices": {
                    "type": "object",
                    "properties":{
                        "a": {
                            "type": 'string',
                            'description': 'choice (a) of the quiz'
                        },
                        "b": {
                            "type": 'string',
                            'description': 'choice (b) of the quiz'
                        },
                        "c": {
                            "type": 'string',
                            'description': 'choice (c) of the quiz'
                        },
                    },
                    "description": f"A few choices for question {id+1} where only one is correct. (using mathjax $ maths notation)",
                },
                "answer": {
                    "type": "object",
                    "properties":{
                        "correct_choice": {
                            "type": 'string',
                            'description': f'The correct choice for question {id}'
                        },
                        "answer": {
                            "type": 'string',
                            'description': f'A step by step explanation of the answer to question {id}, this explains the steps taken to get the correct choice'
                        },
                    },
                    "description": f"A detailed step by step answer to the question {id+1} in the multiple choice quiz, this is an explanation of the resoning behind the solution. (using mathjax $ maths)",
                }
            }
        }
        for id in range(n_questions)
    ]
    function_description = {
        "name": "create_a_quiz",
        "description": "Create a multiple choice quiz, test or examination, from the supplied values, this function is used when a test/quiz or a short examination is requested.",
        "parameters": {
            "type": "object",
            "properties": {
                "quiz_introduction": {
                    "type": "string",
                    "description": "An fun introduction to the quiz, that challanges the student to perform well.",
                },
            },
            "required": [
                "quiz_introduction", "quiz",
            ],
        },
    }
    function_description['parameters']['properties']['quiz'] = {}
    function_description['parameters']['properties']['quiz']['type'] = "object"
    function_description['parameters']['properties']['quiz']['properties'] = {}
    function_description['parameters']['properties']['quiz']['description'] = "The quiz requested is outlined in this value, it contains the questions choices and answers"
    for idd, question_dict in enumerate(function_outline):
        idd += 1
        function_description['parameters']['properties']['quiz']['properties'][idd] = question_dict
    system_message = "Youre a helpful tutor for this student. Your responses are formatted in HTML and MATHJAX ($ for inline maths), the lesson being taught is the following {system_content}."
    return function_description, 'create_a_quiz', system_message


def create_flashcards_function(n_questions):
    function_outline = [
        {
            "type": 'object',
            'properties':{
                "question": {
                    "type": "string",
                    "description": f"Question {id+1} in the multiple choice quiz. (using mathjax $ maths)",
                },
                "choices": {
                    "type": "object",
                    "properties":{
                        "a": {
                            "type": 'string',
                            'description': 'choice (a) of the quiz'
                        },
                        "b": {
                            "type": 'string',
                            'description': 'choice (b) of the quiz'
                        },
                        "c": {
                            "type": 'string',
                            'description': 'choice (c) of the quiz'
                        },
                    },
                    "description": f"A few choices for question {id+1} where only one is correct. (using mathjax $ maths notation)",
                },
                "answer": {
                    "type": "object",
                    "properties":{
                        "correct_choice": {
                            "type": 'string',
                            'description': f'The correct choice for question {id}'
                        },
                        "answer": {
                            "type": 'string',
                            'description': f'A step by step explanation of the answer to question {id}, this explains the steps taken to get the correct choice'
                        },
                    },
                    "description": f"A detailed step by step answer to the question {id+1} in the multiple choice quiz, this is an explanation of the resoning behind the solution. (using mathjax $ maths)",
                }
            }
        }
        for id in range(n_questions)
    ]
    function_description = {
        "name": "create_flashcards",
        "description": "Create a multiple choice quiz, test or examination, from the supplied values, this function is used when a test/quiz or a short examination is requested.",
        "parameters": {
            "type": "object",
            "properties": {
                "quiz_introduction": {
                    "type": "string",
                    "description": "An fun introduction to the quiz, that challanges the student to perform well.",
                },
            },
            "required": [
                "quiz_introduction", "quiz",
            ],
        },
    }
    function_description['parameters']['properties']['quiz'] = {}
    function_description['parameters']['properties']['quiz']['type'] = "object"
    function_description['parameters']['properties']['quiz']['properties'] = {}
    function_description['parameters']['properties']['quiz']['description'] = "The quiz requested is outlined in this value, it contains the questions choices and answers"
    for idd, question_dict in enumerate(function_outline):
        idd += 1
        function_description['parameters']['properties']['quiz']['properties'][idd] = question_dict
    system_message = "Youre a helpful tutor for this student. Your responses are formatted in HTML and MATHJAX ($ for inline maths), the lesson being taught is the following {system_content}."
    return function_description, 'create_flashcards', system_message


def create_essayQuestion_function():
    function_description = {
        "name": "create_essay",
        "description": "Create a point for the content or topic provided",
        "parameters": {
            "type": "object",
            "properties": {
                "point": {
                    "type": "string",
                    "description": "A point teaching the following lesson",
                },
            },
            "required": [
                "point"
            ],
        },
    }
    system_message = "Youre a helpful tutor creating study content"
    return function_description, 'create_essay', system_message


