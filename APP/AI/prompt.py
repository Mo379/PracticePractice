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
