def create_quiz_function(n_questions):
    function_outline = [
            {
            "type": 'object',
            'properties':{
                "question": {
                    "type": "string",
                    "description": f"Question {id+1} in the multiple choice quiz. (using mathjax $ and $$ for maths)",
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
                    "description": f"A few choices for question {id+1} where only one is correct. (using mathjax $ and $$ for maths notation)",
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
                    "description": f"A detailed step by step answer to the question {id+1} in the multiple choice quiz. (using mathjax $ and $$ for maths)",
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
                "question_1", 'choices_1','answer_1',
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
    return function_description

print(create_quiz_function(5))
