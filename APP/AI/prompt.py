import os
import openai
from decouple import config as decouple_config
import json
import aiohttp

class Prompter:
    def __init__(self, model='gpt-3.5-turbo'):
        self.model = "gpt-3.5-turbo"
        self.OPENAI_ORG = decouple_config('openai_org')
        self.OPENAI_SECRET = decouple_config('openai_secret')
        openai.organization = self.OPENAI_ORG
        openai.api_key = self.OPENAI_SECRET
        self.system_prompts = {
                'course_introductions': "Respond only in pure json format.",
                'course_content_question': "Respond only in a pure json format.the question list can have a difficulty level between 1 and 5,level 1 questions are usually those found at the start of a beginner topic, while level 5 are exam level questions and are usually very difficultand rigorous, the other levels are slow step ups in difficulty to help the student learn efficently, each question can include multiple parts for example parts (a,b,c) given as a mix between plain text and markdown. The response must be in pure json.",
                'course_content_answer': "Respond only in pure json format.",
                'course_content_point': "Respond only in pure json format. The response should have exactly 1 key (1), the content of this key is a string, it avoids headers and introductions like 'hi' and 'hello' and it goes straight to teaching lesson.",
            }

    #
    def prompt(self, system_prompt_name, chat_history, prompt):
        print('running...')
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

    #
    async def async_prompt(self, system_prompt_name, chat_history, prompt):
        print('running...')
        COMPLETIONS_MODEL = self.model
        request_url = "https://api.openai.com/v1/chat/completions"
        request_header = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.OPENAI_SECRET}"
            }
        sys_prompt = self.system_prompts[system_prompt_name]
        chat = []
        if chat_history:
            chat.append(chat_history)
        chat.append({'role': 'user', 'content': prompt})
        messages=[
            {"role": "system", "content": f"{sys_prompt}"},
            *chat
        ]
        #
        data = {'model': COMPLETIONS_MODEL, 'messages': messages}
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                        url=request_url, headers=request_header, json=data
                    ) as response:
                    resp = await response.json()
                for i in range(5):
                    try:
                        response_content = resp['choices'][0]['message']['content']
                        json.loads(response_content)
                        return resp
                    except Exception:
                        print('fail and regenerate...')
                        async with session.post(
                                url=request_url, headers=request_header, json=data
                            ) as response:
                            resp = await response.json()
        except Exception:
            return 0
