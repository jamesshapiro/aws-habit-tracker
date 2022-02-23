import os
import json
import boto3
import sys
import datetime
import hashlib
import secrets
import time

table_name = os.environ['DDB_TABLE']
ddb_client = boto3.client('dynamodb')
ses_client = boto3.client('ses')
sender = os.environ['SENDER']
unsubscribe_url = os.environ['UNSUBSCRIBE_URL']

def get_user(event):
    if 'test_user' in event:
        return event['test_user']
    return event['request']['userAttributes']['email']

def get_token():
    m = hashlib.sha256()
    m.update(secrets.token_bytes(4096))
    return m.hexdigest()

def lambda_handler(event, context):
    est_time_delta = datetime.timedelta(hours=5)
    now = datetime.datetime.now()
    now -= est_time_delta
    year = str(now.year)
    day = str(now.day).zfill(2)
    month = str(now.month).zfill(2)
    date = f'{year}-{month}-{day}'
    print(f'{event=}')
    email = get_user(event)
    if 'test_user' not in event and event['triggerSource'] != 'PostConfirmation_ConfirmSignUp':
        return event
    three_days_from_now = int( time.time() ) + 259200
    
    default_habits = [
        {
            'habit_name': 'clean-for-10m',
            'habit_display_name': 'Clean for 10m',
            'habit_color': '#b92514',
            'habit_priority': '5',
            'habit_creation_date': date
        },
        {
            'habit_name': 'get-8h-of-sleep',
            'habit_display_name': 'Get 8h of sleep',
            'habit_color': '#2270A1',
            'habit_priority': '1',
            'habit_creation_date': date
        },
        {
            'habit_name': 'exercise',
            'habit_display_name': 'Exercise',
            'habit_color': '#2270A1',
            'habit_priority': '10',
            'habit_creation_date': date
        },
    ]
    unsubscribe_token = get_token()
    ddb_client.put_item(
        TableName=table_name,
        Item={
            'PK1': {'S': 'UNSUBSCRIBE_TOKEN'},
            'SK1': {'S': f'UNSUBSCRIBE_TOKEN#{unsubscribe_token}'},
            'USER': {'S': email}
        }
    )
    response = ddb_client.put_item(
        TableName=table_name,
        Item={
            'PK1':{'S': 'USER#USER'},
            'SK1':{'S': f'USER#{email}'},
            'UNSUBSCRIBED':{'S': 'FALSE'},
            'TIER':{'S': 'FREE'},
            'UNSUBSCRIBE_TOKEN': {'S': f'{unsubscribe_token}'},
            'JOIN_DATE': {'S': date}
        }
    )
    response = ddb_client.put_item(
        TableName=table_name,
        Item={
            'PK1':{'S': 'SUBSCRIBED'},
            'SK1':{'S': email}
        }
    )
    for item in default_habits:
        response = ddb_client.put_item(
            TableName=table_name,
            Item={
                'PK1':{'S': f'USER#{email}#HABIT'},
                'SK1':{'S': f'HABIT#{item["habit_name"]}'},
                'COLOR':{'S': item['habit_color']},
                'PRIORITY':{'S': str(item['habit_priority'])},
                'DISPLAY_NAME':{'S': item['habit_display_name']},
                'CREATION_DATE':{'S': item['habit_creation_date']}
            }
        )
    response_body = {'shalom': 'haverim!'}
    response_code = 201
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
    first_survey_token = get_token()
    survey_link = f'https://survey.githabit.com/?token={first_survey_token}&date_string={date}'
    ddb_client.put_item(
        TableName=table_name,
        Item={
            'PK1': {'S': f'TOKEN'},
            'SK1': {'S': f'TOKEN#{first_survey_token}'},
            'USER': {'S': f'USER#{email}'},
            'DATE_STRING': {'S': date},
            'TTL_EXPIRATION': {'N': str(three_days_from_now)}
        }
    )
    unsubscribe_link = f'{unsubscribe_url}?token={unsubscribe_token}'
    message = f"""
<!DOCTYPE html>
<html lang="en" xmlns="http://www.w3.org/1999/xhtml" xmlns:o="urn:schemas-microsoft-com:office:office">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <meta name="x-apple-disable-message-reformatting">
  <title></title>
  <!--[if mso]>
  <noscript>
    <xml>
      <o:OfficeDocumentSettings>
        <o:PixelsPerInch>96</o:PixelsPerInch>
      </o:OfficeDocumentSettings>
    </xml>
  </noscript>
  <![endif]-->
  <style>
    table, td, div, h1, p {{font-family: Arial, sans-serif;}}
  </style>
</head>
<body style="margin:0;padding:0;">
  <table role="presentation" style="width:100%;border-collapse:collapse;border:0;border-spacing:0;background:#ffffff;">
    <tr>
      <td align="center" style="padding:0;">
        <table role="presentation" style="width:602px;border-collapse:collapse;border:1px solid #cccccc;border-spacing:0;text-align:left;">
          <tr>
            <td align="center" style="padding:40px 0 30px 0;background:#70bbd9;">
              <img src="https://cdkhabits-surveygithabitcombucket4f6ffd5a-1mwnd3a635op9.s3.amazonaws.com/cropped.png" alt="" width="300" style="height:auto;display:block;" />
            </td>
          </tr>
          <tr>
            <td style="padding:36px 30px 42px 30px;">
              <table role="presentation" style="width:100%;border-collapse:collapse;border:0;border-spacing:0;">
                <tr>
                  <td style="padding:0 0 36px 0;color:#153643;">
                    <h1 style="font-size:32px;margin:0 0 0 0;font-family:Arial,sans-serif;line-height:36px;">Thanks for joining GitHabit, the unreasonably effective system for building and tracking good habits!</p>
                    <p style="margin:32px 0 0 0;font-size:36px;line-height:36px;font-family:Arial,sans-serif;">How it works:</p>
                    <ul style="margin:32px 0 0 0;">
                        <li style="margin:0 0 12px 0;font-weight:normal;font-size:30px;line-height:30px;font-family:Arial,sans-serif;">Log into <a href="https://githabit.com/" style="font-weight:bold;color:#ee4c50;text-decoration:underline;">GitHabit</a> to add/remove your habits (we've created a few default ones for you)</li>
                        <li style="margin:0 0 12px 0;font-weight:normal;font-size:30px;line-height:30px;font-family:Arial,sans-serif;">Each night at 11PM Eastern you'll receive a new <a href="{survey_link}" style="font-weight:bold;color:#ee4c50;text-decoration:underline;">survey link</a></li>
                        <li style="margin:0 0 12px 0;font-weight:normal;font-size:30px;line-height:30px;font-family:Arial,sans-serif;">The survey expires 💣</a></li>
                        <li style="margin:0 0 12px 0;font-weight:normal;font-size:30px;line-height:30px;font-family:Arial,sans-serif;">Complete it before time runs out! ⏰</a></li>
                        <li style="margin:0 0 12px 0;font-weight:normal;font-size:30px;line-height:30px;font-family:Arial,sans-serif;">Depending on your timezone <span style="font-size:20px;">🌐</span>, it may take up to 24 hours for daily results to appear on the grid.</a></li>
                        <li style="margin:0 0 12px 0;font-weight:normal;font-size:30px;line-height:30px;font-family:Arial,sans-serif;">Best of luck, and enjoy!</a></li>
                    </ol>
                  </td>
                </tr>
              </table>
            </td>
          </tr>
          <tr>
            <td style="padding:30px;background:#ee4c50;">
              <table role="presentation" style="width:100%;border-collapse:collapse;border:0;border-spacing:0;font-size:9px;font-family:Arial,sans-serif;">
                <tr>
                  <td style="padding:0;width:50%;" align="left">
                    <p style="margin:0;font-size:14px;line-height:16px;font-family:Arial,sans-serif;color:#ffffff;">
                      GitHabit {year}<br/><a href="{unsubscribe_link}" style="color:#ffffff;text-decoration:underline;">Unsubscribe</a>
                    </p>
                  </td>
                  <td style="padding:0;width:50%;" align="right">
                    <table role="presentation" style="border-collapse:collapse;border:0;border-spacing:0;">
                      <tr>
                        <td style="padding:0 0 0 10px;width:38px;">
                          <a href="https://githabit.com/" style="color:#ffffff;"><img src="https://cdkhabits-surveygithabitcombucket4f6ffd5a-1mwnd3a635op9.s3.amazonaws.com/blue-rabbit.png" alt="GitHabit" width="38" style="height:auto;display:block;border:0;" /></a>
                        </td>
                      </tr>
                    </table>
                  </td>
                </tr>
              </table>
            </td>
          </tr>
        </table>
      </td>
    </tr>
  </table>
</body>
</html>
"""
    response = ses_client.send_email(
        Source= f'GitHabit.com <{sender}>',
        Destination={
            'ToAddresses': [
                email
            ]
        },
        Message={
            'Subject': {
                'Data': f'👋🐇 Welcome to GitHabit!'
            },
            'Body': {
                'Html': {
                    'Data': message
                }
            }
        }
    )
    return event