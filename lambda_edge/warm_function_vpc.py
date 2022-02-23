import boto3
import os
import requests
import datetime
import json

cognito_client = boto3.client('cognito-idp')
website_url =   os.environ['WEBSITE_URL']
test_username = os.environ['TEST_USERNAME']
test_password = os.environ['TEST_PASSWORD']
user_pool_id =  os.environ['USER_POOL_ID']
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
    username, password, 
    user_pool_id, app_client_id
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

def lambda_handler(event, context):
    #print('shalom haverim!')
    id_token = authenticate_and_get_token(
        test_username, test_password, 
        user_pool_id, app_client_id
    )
    headers = {'Authorization':  'Bearer ' + id_token}
    r = requests.get(f'https://{website_url}')
    #print(r.text)
    # GET habit list
    invoke_url = f'{api_url_base}/prod/habit-auth/'
    r = requests.get(invoke_url, headers=headers)
    #print(r.text)
    # GET habit data
    invoke_url = f"""{api_url_base}/prod/habit-data-auth/?user={test_username}&PK1=clean-for-10m&limit=373&startkey={get_todays_date()}"""
    #print(invoke_url)
    r = requests.get(invoke_url, headers=headers)
    #print(r.text)
    return graceful_exit()
