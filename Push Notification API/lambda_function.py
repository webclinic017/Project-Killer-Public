#notifications.py

import requests
from oauth2client.service_account import ServiceAccountCredentials
import json


def _get_access_token():
    credentials = ServiceAccountCredentials.from_json_keyfile_name(
        'fb_credentials.json',
        ['https://www.googleapis.com/auth/firebase.messaging'])
    access_token_info = credentials.get_access_token()
    return access_token_info.access_token


def send_notification(title, body, token):
    url = 'https://fcm.googleapis.com/v1/projects/killer-interface/messages:send'
    fcm_message = {'message': {
        'token': token,
        'notification': {
            'title': title,
            'body': body
        },
        'apns': {
            'payload': {
                'aps': {
                    'sound': "alert.wav"
                }
            }
        }
    }
    }

    headers = {
        'Authorization': 'Bearer ' + _get_access_token(),
        'Content-Type': 'application/json; UTF-8',
    }
    response_error = None
    try:
        response = requests.post(url, data=json.dumps(fcm_message), headers=headers)
        print(response.json())
        response.raise_for_status()
    except Exception as e:
        response_error = e
        print(response_error)



def lambda_handler(event, context):
    if event['rawPath'] == '/send_notification':
        token = event['queryStringParameters']['token']
        title = event['queryStringParameters']['title']
        body = event['queryStringParameters']['body']
        send_notification(title, body, token)
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
