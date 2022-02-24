import boto3
import os
import requests
import datetime
import json
import asyncio
import time

cognito_client = boto3.client('cognito-idp')
website_url =   os.environ['WEBSITE_URL']
test_username = os.environ['TEST_USERNAME']
test_password = os.environ['TEST_PASSWORD']
app_client_id = os.environ['APP_CLIENT_ID']
api_url_base =  os.environ['API_URL']

def graceful_exit():
    response_code = 200
    response = {
        'statusCode': response_code,
        'body': json.dumps({'shalom': 'haverim!'})
    }
    return response

def get_todays_date():
    est_time_delta = datetime.timedelta(hours=19)
    now = datetime.datetime.now()
    now += est_time_delta
    year = str(now.year)
    day = str(now.day).zfill(2)
    month = str(now.month).zfill(2)
    date = f'{year}-{month}-{day}'
    return date

def authenticate_and_get_token(
    username, password, app_client_id
):
    response = cognito_client.initiate_auth(
        ClientId=app_client_id,
        AuthFlow='USER_PASSWORD_AUTH',
        AuthParameters={
            "USERNAME": username,
            "PASSWORD": password
        }
    )
    return response['AuthenticationResult']['IdToken']

def run_command(x):
    start = time.time()
    #print(f'starting {x["url"][:71]}')
    r = requests.get(url=x['url'], headers=x['headers'])
    #print(f'stopping {x["url"][:71]}')
    end = time.time()
    #print(f'{end - start:.2f} GET {x["url"][:71]}')
    return r


async def main(id_token):
    headers = {'Authorization':  'Bearer ' + id_token}
    loop = asyncio.get_event_loop()
    futures = [
        loop.run_in_executor(
            None, 
            lambda: run_command({'url': f'https://{website_url}', 'headers': {}})
        ),
        loop.run_in_executor(
            None, 
            lambda: run_command({'url': f'{api_url_base}/prod/habit-auth/', 'headers': headers})
        ),
        loop.run_in_executor(
            None, 
            lambda: run_command({'url': f"""{api_url_base}/prod/habit-data-auth/?user={test_username}&PK1=clean-for-10m&limit=373&startkey={get_todays_date()}""", 'headers': headers})
        )
    ]
    for response in await asyncio.gather(*futures):
        pass

def lambda_handler(event, context):
    id_token = authenticate_and_get_token(
        test_username, test_password, 
        app_client_id
    )
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(id_token))
    return graceful_exit()

