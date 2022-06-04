import enum
import credentials
import time


class Account(enum.Enum):
    one = 1

    def key(self):
        creds = credentials.decoded_credentials
        if self == Account.one:
            return creds["PHEMEX_API_KEY_1"]

    def secret(self):
        creds = credentials.decoded_credentials
        if self == Account.one:
            return creds["PHEMEX_API_SECRET_1"]
