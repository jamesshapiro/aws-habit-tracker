import os
import json
import boto3
import datetime
import hashlib
import secrets
import time

table_name = os.environ['DDB_TABLE']
user_pool_id = os.environ['USER_POOL_ID']

ses_client = boto3.client('ses')
ddb_client = boto3.client('dynamodb')
user_pool_id = os.environ['USER_POOL_ID']

cognito_idp_client = boto3.client('cognito-idp')
paginator = cognito_idp_client.get_paginator('list_users')
sender = 'githabitsurvey@gmail.com'

def get_users():
    response_iterator = paginator.paginate(
        UserPoolId=user_pool_id,
        AttributesToGet=['email']
    )
    emails = []
    for users in response_iterator:
        users_users = users['Users']
        email_batch = [item['Attributes'][0]['Value'] for item in users_users]
        emails.extend(email_batch)
    return emails

def lambda_handler(event, context):
    three_days_from_now = int( time.time() ) + 259200
    est_time_delta = datetime.timedelta(hours=5)
    users = get_users()
    for user in users:
        print(f'{user=}')
        print(f'Habit Survey <{sender}>')
        now = datetime.datetime.now()
        now -= est_time_delta
        m = hashlib.sha256()
        m.update(secrets.token_bytes(4096))
        sha256 = m.hexdigest()
        year = str(now.year)
        day = str(now.day).zfill(2)
        month = str(now.month).zfill(2)
        message = f'habits-survey.weakerpotions.com/?token={sha256}&date_string={year}-{month}-{day}'
        ddb_client.put_item(
            TableName=table_name,
            Item={
                'PK1': {'S': f'TOKEN'},
                'SK1': {'S': f'TOKEN#{sha256}'},
                'USER': {'S': f'USER#{user}'},
                'DATE_STRING': {'S': f'{year}-{month}-{day}'},
                'TTL_EXPIRATION': {'N': str(three_days_from_now)}
            }
        )

        response = ses_client.send_email(
            Source= f'Habit Survey <{sender}>',
            Destination={
                'ToAddresses': [
                    user
                ]
            },
            Message={
                'Subject': {
                    'Data': f'HABITS SURVEY: {month}-{day}-{year}'
                },
                'Body': {
                    'Text': {
                        'Data': message
                    }
                }
            }
        )
    print(f'{response=}')
    return {
        'statusCode': 200,
        'body': 'shalom haverim!'
    }
