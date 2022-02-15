import os
import json
import boto3
import requests
from bs4 import BeautifulSoup

table_name = os.environ['DDB_TABLE']
ddb_client = boto3.client('dynamodb')

def grab_data(url):
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    return [(elem.attrs['data-date'], elem.attrs['data-count']) for elem in soup.find_all("rect", class_="ContributionCalendar-day") if 'data-count' in elem.attrs]

def lambda_handler(event, context):
    print(f'{event=}')
    body = event['body']
    print(f'{body=}')
    habits_user = body['habits_user']
    github_username = body['github_user']
    url = f'https://github.com/{github_username}'
    response = ddb_client.put_item(
        TableName=table_name,
        Item={
            'PK1': {'S': f'USER#{habits_user}#HABIT'},
            'SK1': {'S': f'HABIT#commit-to-github'},
            'PRIORITY': {'S': '90'},
            'COLOR': {'S': '#216e39'}
        }
    )

    for date, count in grab_data(url):
        response = ddb_client.put_item(
            TableName=table_name,
            Item={
                'PK1': {'S': f'USER#{habits_user}#HABIT#commit-to-github'},
                'SK1': {'S': f'DATE#{date}'},
                'DATE_COUNT': {'S': str(count)},
                'DATE_LEVEL': {'S': str(count)}
            }
        )

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