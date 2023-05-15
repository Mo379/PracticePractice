course_introductions = 'Respond only in pure json format.'


def course_introduction_prompt(course_name, course_level, course_spec_subject, context):
    return f"Create a json response with 3 keys (course_skills, \
course_summary and course_learning_objectives), the course_skills and \
course_learning_objectives are lists with exactly 6 entries each with each \
item in the list being a string and the summary is simply \
a string, the summary should be very informative while being short, and should\
get the student exited about the course. The values are for a course named {course_name}, has \
difficulty level of '{course_level}', and the \
course subject is {course_spec_subject}. Use the following chapters list \
to create an informative summary \n\n{context}"


course_content_question = "Respond only in a pure json format.the question \
list can have a difficulty level between 1 and 5, level 1 questions are usually \
those found at the start of a beginner topic, while level 5 are exam level \
questions and are usually very difficult and rigorous, the other levels are \
slow step ups in difficulty to help the student learn efficently. \
The response must be in pure json, the text is in markdown and MATHJAX."


def questions_prompt(level, subject, module, chapter, prompt_level, text):
    return f"Create a json response with exactly 5 keys (1, 2, 3, 4, 5) \
where the content for each key is simply a string. \
the string for each of the keys is an exam style question, this \
is for a course staged in '{level}', where the subject is {subject}, \
the module for the questions is {module} and the chapter is {chapter}, \
the questions are of increasing difficulty and arranged in such \
a way that is easy for a beginner to build their understanding, \
overall the difficult of this list of qustions is of level {prompt_level}. \
The instructor provided the following context to help guide the style and content \
of the question, thus the question content should closely follow it with combination \
with the previous context. \n\n ('instructor_context':'{text}')."


course_content_answer = "Respond only in pure json format. Utilising markdown\
and MATHJAX where appropriate."


def answers_prompt(question):
    return f"For the following question, find a step by step solution \n\n \
{question}"


course_content_point = "Respond only in pure json format. The response should \
have exactly 1 key (1), the content of this key is a string, it avoids headers \
and introductions like 'hi' and 'hello' and it goes straight to teaching \
lesson. The response must be in pure json, the text is in markdown and MATHJAX."


def points_prompt(level, subject, module, chapter, point_title, topic_text, point_text):
    return f"For a course staged in '{level}', the subject is {subject}, \
the module for content is {module} and the chapter is {chapter}, \
create a short lesson for the lesson point titled '{point_title}', that \
teaches this in a way that is easy \
to build an understanding, use the following \
context that to help with the content of the lesson, \
('context_1':'{topic_text}', 'context_2':'{point_text}')."
