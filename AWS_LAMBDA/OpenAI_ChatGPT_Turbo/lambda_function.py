import os
import openai
import json
import markdown

OPENAI_ORG = os.environ['openai_org']
OPENAI_SECRET = os.environ['openai_secret']
openai.organization = OPENAI_ORG
openai.api_key = OPENAI_SECRET
import os
import openai
import json
import requests

OPENAI_ORG = os.environ['openai_org']
OPENAI_SECRET = os.environ['openai_secret']
openai.organization = OPENAI_ORG
openai.api_key = OPENAI_SECRET

def lambda_handler(event, context):
    # TODO implement
    model = event['message']['model']
    system = event['message']['system']
    chat = event['message']['chat']
    response = openai.ChatCompletion.create(
        model=model,
        messages=[
            {"role": "system", "content": system},
            *chat
        ]
    )
        # Send POST request to your website
    url = 'https://www.practicepractice.net/AI/_catch_chat_completion'  # Replace with your website URL
    data = {
        'part_id': event['part_id'],
        'point_id': event['point_id'],
        'global_order_id': event['global_order_id'],
        'local_order_id': event['local_order_id'],
        'prompt_tokens': response["usage"]['prompt_tokens'],
        'completion_tokens': response["usage"]['completion_tokens'],
        'otal_tokens': response["usage"]['total_tokens'],
        'user_prompt': event['user_prompt'],
        'ai_response': response["choices"][0]["message"]["content"],
    }
    headers = {'Content-Type': 'application/json'}
    my_response = requests.post(url, json=data, headers=headers)
    if my_response.status_code == 200:
        server_records = 1
    else:
        server_records = 0
    #
    html = markdown.markdown(response["choices"][0]["message"]["content"], extensions=['tables','admonition'])
    #
    return {
        'StatusCode': 200,
        'body': response["choices"][0]["message"]["content"],
        'html_body': html,
        'usage': response["usage"],
        'server_records': server_records,
    }
