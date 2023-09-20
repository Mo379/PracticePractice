import collections
from content.util.GeneralUtil import (
        order_full_spec_content,
        order_live_spec_content
    )
from content.models import Course, Question, Point
from user.models import User


def create_course_point():
    function_description = {
        "name": "create_course_point",
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
    return function_description, 'create_course_point', system_message


def create_course_questions(n_questions=5):
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
                    "description": f"A detailed step by step answer to question {id+1}, this is an explanation of the resoning behind the solution. (using mathjax $ maths)",
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
            },
            "required": [
                "questions"
            ],
        },
    }
    function_description['parameters']['properties']['questions'] = {}
    function_description['parameters']['properties']['questions']['type'] = "object"
    function_description['parameters']['properties']['questions']['properties'] = {}
    function_description['parameters']['properties']['questions']['description'] = "The questions requested is outlined in this value, it contains the questions and answers"
    for idd, question_dict in enumerate(function_outline):
        idd += 1
        function_description['parameters']['properties']['quiz']['properties'][idd] = question_dict
    system_message = "Youre a helpful tutor creating questions and answers for students."
    return function_description, 'create_course_questions', system_message


def create_course_introduction(user, course, n_skills=10):
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


