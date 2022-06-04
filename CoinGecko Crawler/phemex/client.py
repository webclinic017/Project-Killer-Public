import hmac
import hashlib
import json
import requests
import time

from math import trunc
from .exceptions import PhemexAPIException


class Client(object):

    MAIN_NET_API_URL = 'https://api.phemex.com'
    TEST_NET_API_URL = 'https://testnet-api.phemex.com'

    def __init__(self):
        self.account = None
        self.api_key = None
        self.api_secret = None
        self.api_URL = None
        self.session = requests.session()

    def update_client(self, acct, is_testnet=False):
        self.account = acct
        self.api_key = self.account.key()
        self.api_secret = self.account.secret()
        self.api_URL = self.MAIN_NET_API_URL
        if is_testnet:
            self.api_URL = self.TEST_NET_API_URL

    def _send_request(self, method, endpoint, params={}, body={}):
        expiry = str(trunc(time.time()) + 60)
        query_string = '&'.join(['{}={}'.format(k,v) for k,v in params.items()])
        message = endpoint + query_string + expiry
        body_str = ""
        if body:
            body_str = json.dumps(body, separators=(',', ':'))
            message += body_str
        signature = hmac.new(self.api_secret.encode('utf-8'), message.encode('utf-8'), hashlib.sha256)
        self.session.headers.update({
            'x-phemex-request-signature': signature.hexdigest(),
            'x-phemex-request-expiry': expiry,
            'x-phemex-access-token': self.api_key,
            'Content-Type': 'application/json'})

        url = self.api_URL + endpoint
        if query_string:
            url += '?' + query_string
        response = self.session.request(method, url, data=body_str.encode())
        if not str(response.status_code).startswith('2'):
            raise PhemexAPIException(response)
        try:
            res_json = response.json()
        except ValueError:
            raise PhemexAPIException('Invalid Response: %s' % response.text)
        ok_codes = [0, 10002, 11074]
        if "code" in res_json and res_json["code"] not in ok_codes:
            raise PhemexAPIException(response)
        if "error" in res_json and res_json["error"]:
            raise PhemexAPIException(response)
        return res_json

    def public_info(self):
        return self._send_request("GET", "/public/products")
