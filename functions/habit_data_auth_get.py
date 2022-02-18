import os
import json
import boto3

table_name = os.environ['DDB_TABLE']
ddb_client = boto3.client('dynamodb')

def lambda_handler(event, context):
    #print(f'{event=}')
    email = event['requestContext']['authorizer']['claims']['email']
    query_string_parameters = event['queryStringParameters']
    habit_name = query_string_parameters['PK1']
    limit = int(query_string_parameters['limit'])
    start_key = query_string_parameters['startkey']
    response = ddb_client.query(
        TableName=table_name,
        KeyConditionExpression='#pk1=:pk1',
        ExpressionAttributeNames={'#pk1':'PK1'},
        ExpressionAttributeValues={':pk1':{'S':f'USER#{email}#HABIT#{habit_name}'}},
        ExclusiveStartKey={
            'PK1':{'S':f'USER#{email}#HABIT#{habit_name}'},
            'SK1':{'S':f'DATE#{start_key}'}
        },
        Limit=limit,
        ScanIndexForward=False
    )
    response_body = response
    response_code = 200
    response = {
        'statusCode': response_code,
        'headers': {
            'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,X-Amz-Security-Token,Authorization,X-Api-Key,X-Requested-With,Accept,Access-Control-Allow-Methods,Access-Control-Allow-Origin,Access-Control-Allow-Headers',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'DELETE,GET,HEAD,OPTIONS,PATCH,POST,PUT',
            'X-Requested-With': '*'
        },
        'body': json.dumps(response_body)
    }
    return response