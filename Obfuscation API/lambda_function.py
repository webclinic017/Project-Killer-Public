# lambda_function.py

import json
import time

import requests

import firebase as ref


def decode(string):
    ct = len(string) + 17
    new = ""
    for code in map(ord, string):
        ct -= 1
        asc = code + ct
        if asc >= 126:
            asc -= 94
        back = chr(asc)
        new += back
    return new


def encode(string):
    ct = len(string) + 17
    new = ""
    for code in map(ord, string):
        ct -= 1
        asc = code - ct
        if asc - 32 <= 0:
            asc += 94
        back = chr(asc)
        if back == "\\":
            back = "\\"
        new += back
    return new


def validate(event):
    if 'rawPath' in event:
        if event['rawPath'] != "/Decode" and event['rawPath'] != "/Encode":
            return {'statusCode': 405, 'body': json.dumps("Validation Error: Incorrect Endpoint")}
    else:
        return {'statusCode': 405, 'body': json.dumps("Validation Error: No endpoint specified")}
    if 'queryStringParameters' in event:
        qsp = event['queryStringParameters']
        if 'keys' not in qsp:
            return {'statusCode': 405, 'body': json.dumps("Validation Error: keys parameter is empty")}
        if 'passkey' not in qsp:
            return {'statusCode': 405, 'body': json.dumps("Validation Error: passkey parameter is empty")}
        else:
            passkey = qsp['passkey']
            if passkey != "!!@#$#it'snotjustforbreakfastN@@nBr3@d&Butt3rCh!ck3n":
                return {'statusCode': 405, 'body': json.dumps("Validation Error: passkey has the incorrect value")}
        if 'time' not in qsp:
            return {'statusCode': 405, 'body': json.dumps("Validation Error: time parameter is empty")}
        else:
            param_time = int(qsp['time'])
            if type(param_time) != int:
                return {'statusCode': 405, 'body': json.dumps("Validation Error: time must be type int")}
            ref_time = int(ref.get_data("Obfuscation/time").json())
            current_time = int(time.time())
            if (ref_time != param_time) or (ref_time - 3 >= current_time) or (current_time >= ref_time + 3):
                return {'statusCode': 405, 'body': json.dumps("Validation Error: time cannot be validated")}
    else:
        return {'statusCode': 405, 'body': json.dumps("Validation Error: No parameters specified")}
    access = ref.get_data("Obfuscation/access").json()
    if not access:
        return {'statusCode': 405, 'body': json.dumps("Access Denied")}
    return None


def grab_relevant_keys(all_keys):
    url = "https://8fulquviti.execute-api.us-east-2.amazonaws.com/find"
    params = {
        "keys": all_keys
    }
    response = requests.get(url, params)
    print(response.json())
    return response.json()


def lambda_handler(event, context):
    validation = validate(event)
    if validation is None:
        raw_path = event['rawPath']
        if raw_path == "/Decode":
            all_keys = json.loads(event['queryStringParameters']['keys'])
            loaded = grab_relevant_keys(all_keys)
            n = 99

            return_dict = {}

            for key in loaded:
                string = loaded[key]
                pieces = ""
                chunks = [string[i:i + n] for i in range(0, len(string), n)]

                for chunk in chunks:
                    pieces += decode(chunk)

                return_dict[key] = pieces

            return {'statusCode': 200, 'body': json.dumps(return_dict)}
        elif raw_path == "/Encode":
            loaded = json.loads(event['queryStringParameters']['keys'])
            n = 99

            return_dict = {}

            for key in loaded:
                string = loaded[key]
                pieces = ""
                chunks = [string[i:i + n] for i in range(0, len(string), n)]

                for chunk in chunks:
                    pieces += encode(chunk)

                return_dict[key] = pieces

            return {'statusCode': 200, 'body': json.dumps(return_dict)}
    else:
        return validation
