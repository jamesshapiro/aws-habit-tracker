import os
import json
import boto3
import datetime
import hashlib
import secrets
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

table_name = os.environ['DDB_TABLE']

ses_client = boto3.client('ses')
ddb_client = boto3.client('dynamodb')
unsubscribe_url = os.environ['UNSUBSCRIBE_URL']

months = {
    '01': 'January',
    '02': 'February',
    '03': 'March',
    '04': 'April',
    '05': 'May',
    '06': 'June',
    '07': 'July',
    '08': 'August',
    '09': 'September',
    '10': 'October',
    '11': 'November',
    '12': 'December'
}

days = { 
    '01':'1st', '02':'2nd',
    '03':'3rd', '04':'4th',
    '05':'5th', '06':'6th',
    '07':'7th', '08':'8th',
    '09':'9th', '10':'10th',
    '11':'11th', '12':'12th',
    '13':'13th', '14':'14th',
    '15':'15th', '16':'16th',
    '17':'17th', '18':'18th',
    '19':'19th', '20':'20th',
    '21':'21st', '22':'22nd',
    '23':'23rd', '24':'24th',
    '25':'25th', '26':'26th',
    '27':'27th', '28':'28th',
    '29':'29th', '30':'30th',
    '31':'31st'
}

paginator = ddb_client.get_paginator('query')
sender = os.environ['SENDER']

def get_subscribers(event):
    if 'user' in event:
        return [event['user']]
    response_iterator = paginator.paginate(
        TableName=table_name,
        KeyConditionExpression='#pk1=:pk1',
        ExpressionAttributeNames={'#pk1':'PK1'},
        ExpressionAttributeValues={':pk1':{'S':f'SUBSCRIBED'}}
    )
    subscribers = []
    for items in response_iterator:
        subscriber_page = [item['SK1']['S'] for item in items['Items']]  
        subscribers.extend(subscriber_page)
    return subscribers

def get_token():
    m = hashlib.sha256()
    m.update(secrets.token_bytes(4096))
    return m.hexdigest()

def lambda_handler(event, context):
    three_days_from_now = int( time.time() ) + 259200
    est_time_delta = datetime.timedelta(hours=5)
    subscribers = get_subscribers(event)
    print(f'{subscribers=}')
    for subscriber in subscribers:
        print(f'{subscriber=}')
        print(f'Habit Survey <{sender}>')
        now = datetime.datetime.now()
        now -= est_time_delta
        sha256 = get_token()
        year = str(now.year)
        day = str(now.day).zfill(2)
        month = str(now.month).zfill(2)
        survey_link = f'https://survey.githabit.com/?token={sha256}&date_string={year}-{month}-{day}'
        ddb_client.put_item(
            TableName=table_name,
            Item={
                'PK1': {'S': f'TOKEN'},
                'SK1': {'S': f'TOKEN#{sha256}'},
                'USER': {'S': f'USER#{subscriber}'},
                'DATE_STRING': {'S': f'{year}-{month}-{day}'},
                'TTL_EXPIRATION': {'N': str(three_days_from_now)}
            }
        )
        unsubscribe_token = ddb_client.get_item(TableName=table_name,Key={'PK1': {'S': 'USER#USER'}, 'SK1': {'S': f'USER#{subscriber}'}})['Item']['UNSUBSCRIBE_TOKEN']['S']
        unsubscribe_link = f'{unsubscribe_url}?token={unsubscribe_token}'
        email_day = days[day]
        email_month = months[month]
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
                    <h1 style="font-size:40px;margin:0 0 20px 0;font-family:Arial,sans-serif;">Today's Habit Survey!</h1>
                    <p style="margin:40px 0 0 0;font-size:36px;line-height:30px;font-family:Arial,sans-serif;">Click <a href="{survey_link}" style="font-weight:bold;color:#ee4c50;text-decoration:underline;">HERE</a> to fill it out
                  </td>
                </tr>
                <tr>
                  <td style="padding:0 0 0 0;color:#153643;">
                    <li style="margin:0 0 12px 0;font-size:30px;line-height:24px;font-family:Arial,sans-serif;">The survey expires 💣</a></li>
                    <li style="margin:0 0 12px 0;font-size:30px;line-height:24px;font-family:Arial,sans-serif;">Complete it before time runs out! ⏰</a></li>
                    <li style="margin:0 0 12px 0;font-size:30px;line-height:24px;font-family:Arial,sans-serif;">Depending on your timezone <span style="font-size:20px;">🌐</span>, it may take up to 24 hours for daily results to appear on the grid.</a></li>
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
        msg = MIMEMultipart()
        msg["Subject"] = f'📆🐇 Habits Survey: {email_month} {email_day}, {year}'
        #msg["From"] = sender
        msg["From"] = f'GitHabit.com <{sender}>'
        msg["To"] = subscriber
        body_txt = MIMEText(message, "html")
        msg.attach(body_txt)
        msg['Reply-To'] = 'GitHabit <yes-reply@mail.githabit.com>'
        mail_unsubscribe_link = 'mailto: unsubscribe@mail.githabit.com?subject=unsubscribe'
        #msg['list-unsubscribe'] = f'<{mail_unsubscribe_link}>, <{unsubscribe_link}>'
        msg.add_header('List-Unsubscribe', f'<{mail_unsubscribe_link}>, <{unsubscribe_link}>')
        msg.add_header('List-Unsubscribe-Post', 'List-Unsubscribe=One-Click')
        response = ses_client.send_raw_email(
            Source = f'GitHabit.com <{sender}>', 
            Destinations = [subscriber],
            RawMessage = {"Data": msg.as_string()}
        )
    print(f'{response=}')
    return {
        'statusCode': 200,
        'body': 'shalom haverim!'
    }
