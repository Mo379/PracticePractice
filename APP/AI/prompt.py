import os
import openai
from decouple import config as decouple_config

class Prompter:
    def __init__(self, model='gpt-3.5-turbo'):
        self.model = "gpt-3.5-turbo"
        OPENAI_ORG = decouple_config('openai_org')
        OPENAI_SECRET = decouple_config('openai_secret')
        openai.organization = OPENAI_ORG
        openai.api_key = OPENAI_SECRET
        self.system_prompts = {
                'course_introductions': "Respond only in pure json format.",
                'course_content_question': "Respond only in pure json format.the question list can have a difficulty level between 1 and 5,level 1 questions are usually those found at the start of a beginner topic, while level 5 are exam level questions and are usually very difficultand rigorous, the other levels are slow step ups in difficulty to help the student learn efficently, each question can include multiple parts for example parts (a,b,c) given as a mix between plain text and markdown",
                'course_content_answer': "Respond only in pure json format.",
                'course_content_point': "Respond only in pure json format.",
            }

    #
    def prompt(self, system_prompt_name, chat_history, prompt):
        sys_prompt = self.system_prompts[system_prompt_name]
        chat = []
        if chat_history:
            chat.append(chat_history)
        chat.append({'role': 'user', 'content': prompt})
        #
        response = openai.ChatCompletion.create(
            model=self.model,
            messages=[
                {"role": "system", "content": f"{sys_prompt}"},
                *chat
            ]
        )
        return response['choices'][0]['message']['content'], response
