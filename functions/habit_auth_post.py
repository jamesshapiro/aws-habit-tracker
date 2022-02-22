import os
import json
import boto3
import sys
import datetime

table_name = os.environ['DDB_TABLE']
ddb_client = boto3.client('dynamodb')

def lambda_handler(event, context):
    now = datetime.datetime.now()
    est_time_delta = datetime.timedelta(hours=5)
    now -= est_time_delta
    year = str(now.year)
    day = str(now.day).zfill(2)
    month = str(now.month).zfill(2)
    date = f'{year}-{month}-{day}'
    email = event['requestContext']['authorizer']['claims']['email']
    print(f'{event=}')
    body = json.loads(event['body'])
    print(f'{body=}')
    to_delete = []
    to_put = []
    for habit in body:
        print(f'{habit=}')
        if habit.get('deletePlanned', False):
            to_delete.append(habit)
        else:
            to_put.append(habit)
    for item in to_delete:
        print(f'deleting {item=}')
        response = ddb_client.delete_item(
            TableName=table_name,
            Key={
                'PK1': {'S': f'USER#{email}#HABIT'},
                'SK1': {'S': f'HABIT#{item["habitName"]}'}
            }
        )
        print(f'{response=}')
    for item in to_put:
        print(f'putting {item=}')
        response = ddb_client.get_item(
            TableName=table_name,
            Key={
                'PK1':{'S': f'USER#{email}#HABIT'},
                'SK1':{'S': f'HABIT#{item["habitName"]}'}
            }
        )
        if 'Item' not in response:
            response = ddb_client.put_item(
                TableName=table_name,
                Item={
                    'PK1':{'S': f'USER#{email}#HABIT'},
                    'SK1':{'S': f'HABIT#{item["habitName"]}'},
                    'COLOR':{'S': item["habitColor"]},
                    'PRIORITY':{'S': str(item["habitPriority"])},
                    'DISPLAY_NAME':{'S': item["habitDisplayName"]},
                    'CREATION_DATE': {'S': date}
                }
            )
            print(f'{response=}')
    response_body = {'shalom': 'haverim!'}
    response_code = 200
    response = {
        'statusCode': response_code,
        'headers': {
            'Access-Control-Allow-Headers': "Content-Type,X-Amz-Date,X-Amz-Security-Token,Authorization,X-Api-Key,X-Requested-With,Accept,Access-Control-Allow-Methods,Access-Control-Allow-Origin,Access-Control-Allow-Headers",
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': "DELETE,GET,HEAD,OPTIONS,PATCH,POST,PUT",
            "X-Requested-With": "*"
        },
        'body': json.dumps(response_body)
    }
    return response