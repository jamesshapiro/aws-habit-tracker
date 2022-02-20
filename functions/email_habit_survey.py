import os
import json
import boto3
import datetime
import hashlib
import secrets
import time
import sys

table_name = os.environ['DDB_TABLE']
user_pool_id = os.environ['USER_POOL_ID']

ses_client = boto3.client('ses')
ddb_client = boto3.client('dynamodb')
user_pool_id = os.environ['USER_POOL_ID']


cognito_idp_client = boto3.client('cognito-idp')
paginator = cognito_idp_client.get_paginator('list_users')
sender = os.environ['SENDER']

def get_users(event):
    if 'user' in event:
        return [event['user']]
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
    print('{event=}')
    three_days_from_now = int( time.time() ) + 259200
    est_time_delta = datetime.timedelta(hours=5)
    users = get_users(event)
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
        survey_link = f'https://survey.githabit.com/?token={sha256}&date_string={year}-{month}-{day}'
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
            Source= f'GitHabit.com <{sender}>',
            Destination={
                'ToAddresses': [
                    user
                ]
            },
            Message={
                'Subject': {
                    'Data': f'🐇 Habits Survey: {month}-{day}-{year} ✔️'
                },
                'Body': {
                    'Html': {
                        'Data': f"""<html><h3>Today's Habit Survey!</h3><p>Click <a href="{survey_link}">here</a> to fill it out. The link will work for a few days, so make sure to complete the survey before time runs out!<br><br>You may need to wait up to 24 hours for results to appear."""
                    }
                }
            }
        )
    print(f'{response=}')
    return {
        'statusCode': 200,
        'body': 'shalom haverim!'
    }
