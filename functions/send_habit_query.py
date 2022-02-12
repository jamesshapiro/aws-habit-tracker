import os
import json
import boto3
import datetime
import ulid

phone_number = os.environ['PHONE_NUMBER']
table_name = os.environ['DDB_TABLE']
sns_client = boto3.client('sns')
topic = os.environ['EMAIL_TOPIC']

def lambda_handler(event, context):
    # NOTE: adjust for your local timezone as necessary
    # -5 is the delta for Eastern Standard Time
    est_time_delta = datetime.timedelta(hours=-5)
    est_tz_object = datetime.timezone(est_time_delta, name="EST")
    now = datetime.datetime.now(est_tz_object)
    my_ulid = ulid.from_timestamp(now)
    year = str(now.year)
    day = str(now.day).zfill(2)
    month = str(now.month).zfill(2)
    habit = 'read for 10m'
    todays_date = f'{year}-{month}-{day}'
    message = f'habits-survey.weakerpotions.com/?ulid={my_ulid}'

    response = sns_client.publish(
        TopicArn=topic,
        Message=message,
        Subject=f'HABITS SURVEY: {month}-{day}-{year}'
    )
    
    response = sns_client.publish(
        PhoneNumber=phone_number,
        Message=message
    )
    print(f'{response=}')
    return {
        'statusCode': 200,
        'body': 'shalom haverim!'
    }