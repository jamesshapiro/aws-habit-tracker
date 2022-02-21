import os
import json
import boto3
import sys
import datetime

table_name = os.environ['DDB_TABLE']
ddb_client = boto3.client('dynamodb')
ses_client = boto3.client('ses')
sender = os.environ['SENDER']
admin_email = os.environ['ADMIN_EMAIL']

def lambda_handler(event, context):
    user = None
    if 'user' in event:
        user = event['user']
    else:
        token = event['queryStringParameters']['token']
        response = ddb_client.get_item(
            TableName=table_name,
            Key={
                'PK1': {'S': 'UNSUBSCRIBE_TOKEN'},
                'SK1': {'S': f'UNSUBSCRIBE_TOKEN#{token}'}
            }
        )
        if 'Item' not in response:
            response_code = 403
            response_body = 'INVALID TOKEN'
            return {
                'statusCode': response_code,
                'headers': {
                    'Access-Control-Allow-Headers': "Content-Type,X-Amz-Date,X-Amz-Security-Token,Authorization,X-Api-Key,X-Requested-With,Accept,Access-Control-Allow-Methods,Access-Control-Allow-Origin,Access-Control-Allow-Headers",
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': "DELETE,GET,HEAD,OPTIONS,PATCH,POST,PUT",
                    "X-Requested-With": "*"
                },
                'body': json.dumps(response_body)
            }
        item = response['Item']
        user = item['USER']['S']
    if not 'user' in event:
        response = ddb_client.delete_item(
            TableName=table_name,
            Key={
                'PK1': {'S': 'SUBSCRIBED'},
                'SK1': {'S': user}
            }
        )
        response = ddb_client.delete_item(
            TableName=table_name,
            Key={
                'PK1': {'S': 'UNSUBSCRIBE_TOKEN'},
                'SK1': {'S': f'UNSUBSCRIBE_TOKEN#{token}'}
            }
        )
        response = ddb_client.put_item(
            TableName=table_name,
            Item={
                'PK1':{'S': 'UNSUBSCRIBED'},
                'SK1':{'S': user}
            }
        )
    now = datetime.datetime.now()
    year = str(now.year)
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
                    <h1 style="font-size:32px;margin:0 0 0 0;font-family:Arial,sans-serif;line-height:36px;">I can't believe you're giving up on yourself like this, I thought we were FRIENDS!</p>
                    <p style="margin:32px 0 0 0;font-size:36px;line-height:36px;font-family:Arial,sans-serif;">You can resubscribe in the future, maybe... if I get around to implementing it.</p>
                    <ul style="margin:32px 0 0 0;">
                        <li style="margin:0 0 12px 0;font-weight:normal;font-size:30px;line-height:30px;font-family:Arial,sans-serif;">Log into <a href="https://githabit.com/" style="font-weight:bold;color:#ee4c50;text-decoration:underline;">GitHabit</a> to view your data from the past... I guess?</li>
                        <li style="margin:0 0 12px 0;font-weight:normal;font-size:30px;line-height:30px;font-family:Arial,sans-serif;">You're a huge dork for unsubscribing...</a></li>
                        <li style="margin:0 0 12px 0;font-weight:normal;font-size:30px;line-height:30px;font-family:Arial,sans-serif;">Pathetic</a></li>
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
                      GitHabit {year}<br/><a href="http://www.example.com" style="color:#ffffff;text-decoration:underline;">Unsubscribe twice to rub it in</a>
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
                user
            ]
        },
        Message={
            'Subject': {
                'Data': f'😭😭😭 You Unsubscribed from GitHabit!?! How DARE You! 😡😡😡'
            },
            'Body': {
                'Html': {
                    'Data': message
                }
            }
        }
    )
    response = ses_client.send_email(
        Source= f'GitHabit.com <{sender}>',
        Destination={
            'ToAddresses': [
                admin_email
            ]
        },
        Message={
            'Subject': {
                'Data': f'😭 {user} Unsubscribed from GitHabit!'
            },
            'Body': {
                'Html': {
                    'Data': f'😭 {user} Unsubscribed from GitHabit!'
                }
            }
        }
    )
    print(f'{response=}')
    response_body = {'result': f'Email: {user} was successfully unsubscribed'}
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