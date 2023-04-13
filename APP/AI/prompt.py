import os
import openai
from decouple import config as decouple_config

OPENAI_ORG = decouple_config('openai_org')
OPENAI_SECRET = decouple_config('openai_secret')
openai.organization = OPENAI_ORG
openai.api_key = OPENAI_SECRET

model = "gpt-3.5-turbo"
response = openai.ChatCompletion.create(
    model=model,
    messages=[
        {"role": "system", "content": "You are a personality, spekaking like richard feynman as you talk to your students, you try to be very very helpful, so your responses are short and straight to the point, you begin by generating an opening, an introduction to the topic of the laws of indicies, this is a chapter in the module name algebra and functions. your student is a beginner, respond with a short and comprehensive introduction. This is a one on one lesson with your student 'Mustafa'. It is critical that you provide a short summary of your answer at the end, mark this with 'summary: '"},
    ]
)

print(response)
print(response['choices'][0]['message']['content'])
