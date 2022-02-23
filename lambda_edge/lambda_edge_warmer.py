import os
import json
import requests

website_url = os.environ['URL']

def exit_gracefully():
    response_code = 200
    response = {
        'statusCode': response_code,
        'body': json.dumps({'shalom': 'haverim!'})
    }
    return response

def lambda_handler(event, context):
    r = requests.get(f'https://{website_url}')
    #print(r.text)
    return exit_gracefully()