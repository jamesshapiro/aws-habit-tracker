import os
import json
import boto3
import sys
import datetime
import hashlib
import secrets
import time

table_name = 'CdkHabits-Habits4519EE09-ILJ7QZQ4JHP3'
ddb_client = boto3.client('dynamodb')
paginator = ddb_client.get_paginator('query')

def get_users():
    response_iterator = paginator.paginate(
        TableName=table_name,
        KeyConditionExpression='#pk1=:pk1',
        ExpressionAttributeNames={'#pk1':'PK1'},
        ExpressionAttributeValues={':pk1':{'S':f'USER#USER'}}
    )
    users = []
    for items in response_iterator:
        user_page = [item['SK1']['S'][len('USER#'):] for item in items['Items']]  
        users.extend(user_page)
    return users

def get_token():
    m = hashlib.sha256()
    m.update(secrets.token_bytes(4096))
    return m.hexdigest()

for user in get_users():
    #print(user)
    if user != 'michaelwellesshapiro@gmail.com':
        continue
    unsubscribe_token = get_token()
    ddb_client.put_item(
        TableName=table_name,
        Item={
            'PK1': {'S': 'UNSUBSCRIBE_TOKEN'},
            'SK1': {'S': f'UNSUBSCRIBE_TOKEN#{unsubscribe_token}'},
            'USER': {'S': user}
        }
    )
    ddb_client.update_item(
        TableName=table_name,
        Key={
            'PK1': {'S': 'USER#USER'},
            'SK1': {'S': f'USER#{user}'}
        },
        UpdateExpression='SET #unsubscribe_token = :unsubscribe_token',
        ExpressionAttributeNames={
            '#unsubscribe_token': 'UNSUBSCRIBE_TOKEN'
        },
        ExpressionAttributeValues={
            ':unsubscribe_token': {'S': unsubscribe_token}
        }
    )
