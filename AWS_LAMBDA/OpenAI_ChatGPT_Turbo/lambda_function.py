import os
import openai
import json

OPENAI_ORG = os.environ['openai_org']
OPENAI_SECRET = os.environ['openai_secret']
openai.organization = OPENAI_ORG
openai.api_key = OPENAI_SECRET

def lambda_handler(event, context):
    # TODO implement
    response = openai.ChatCompletion.create(
        model='gpt-3.5-turbo',
        messages=[
            {"role": "system", "content": f"Youre a helpful assistant"},
            {"role": "user", "content": "Who is newton issac ?"}
        ]
    )
    return {
        'statusCode': 200,
        'body': response
    }

