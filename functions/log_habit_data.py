import os
import json
import ulid
import boto3

table_name = os.environ['DDB_TABLE']
ddb_client = boto3.client('dynamodb')

def lambda_handler(event, context):
    body = json.loads(event['body'])
    my_ulid = ulid.from_str(body['ulid'])
    entry_datetime = my_ulid.timestamp().datetime
    mm = f'{entry_datetime.month:02}'
    dd = f'{entry_datetime.day:02}'
    yyyy = entry_datetime.year
    print(f'{body=}')
    for habit_name in body:
        if habit_name == 'ulid':
            continue
        print(f'{habit_name=}')
        print(f'DATE#{yyyy}-{mm}-{dd}')
        level = body[habit_name] - 1
        count = body[habit_name] - 1
        response = ddb_client.put_item(
            TableName=table_name,
            Item={
                'PK1': {'S': f'HABIT#{habit_name}'},
                'SK1': {'S': f'DATE#{yyyy}-{mm}-{dd}'},
                'DATE_COUNT': {'S': str(count)},
                'DATE_LEVEL': {'S': str(level)}
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