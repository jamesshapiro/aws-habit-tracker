import os
import json
import boto3

table_name = os.environ['DDB_TABLE']
ddb_client = boto3.client('dynamodb')

def lambda_handler(event, context):
    query_string_parameters = event['queryStringParameters']
    token = query_string_parameters['token']
    response = ddb_client.get_item(
        TableName=table_name,
        Key={
            'PK1': {'S': f'TOKEN'},
            'SK1': {'S': f'TOKEN#{token}'}
        }
    )
    item = response['Item']
    user = item['USER']['S'][len('USER#'):]
    response = ddb_client.query(
        TableName=table_name,
        KeyConditionExpression='#pk1=:pk1',
        ExpressionAttributeNames={'#pk1':'PK1'},
        ExpressionAttributeValues={':pk1':{'S':f'USER#{user}#HABIT'}}
    )
    #print(f'{response=}')
    response_body = response['Items']
    response_body = sorted(response_body, key=lambda x: int(x['PRIORITY']['S']), reverse=True)
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