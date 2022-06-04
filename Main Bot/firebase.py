# firebase.py

import requests
import json


def update_firebase(directory, value):
    url = "https://killer-interface-default-rtdb.firebaseio.com/" + directory + ".json"
    headers = {'content-type': 'application/json; charset=UTF-8'}
    data = requests.put(url, headers=headers, data=json.dumps(value).encode("utf-8"))
    return data


def get_data(directory):
    url = "https://killer-interface-default-rtdb.firebaseio.com/" + directory + ".json"
    headers = {'content-type': 'application/json; charset=UTF-8'}
    data = requests.get(url, headers=headers)
    return data


def delete_data(directory):
    url = "https://killer-interface-default-rtdb.firebaseio.com/" + directory + ".json"
    headers = {'content-type': 'application/json; charset=UTF-8'}
    data = requests.delete(url, headers=headers)
    return data