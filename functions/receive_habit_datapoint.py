import os
import json
        
def lambda_handler(event, context):
    print(f'{event=}')
    records = event['Records']
    first_record = records[0]
    print(f'{first_record=}')
    return {
        'statusCode': 200,
        'body': 'shalom haverim!'
    }