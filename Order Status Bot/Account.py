import enum
import credentials
import time


def all_enums(mock):
    if mock:
        return [Account.test_one, Account.test_two, Account.test_three, Account.test_four]
    else:
        return [Account.one, Account.two, Account.three, Account.four]


class Account(enum.Enum):
    one = 1
    two = 2
    three = 3
    four = 4
    test_one = 5
    test_two = 6
    test_three = 7
    test_four = 8

    def key(self):
        creds = credentials.decoded_credentials
        if self == Account.one:
            return creds["PHEMEX_API_KEY_1"]
        elif self == Account.two:
            return creds["PHEMEX_API_KEY_2"]
        elif self == Account.three:
            return creds["PHEMEX_API_KEY_3"]
        elif self == Account.four:
            return creds["PHEMEX_API_KEY_4"]
        elif self == Account.test_one:
            return creds["PHEMEX_TESTNET_API_KEY_1"]
        elif self == Account.test_two:
            return creds["PHEMEX_TESTNET_API_KEY_2"]
        elif self == Account.test_three:
            return creds["PHEMEX_TESTNET_API_KEY_3"]
        elif self == Account.test_four:
            return creds["PHEMEX_TESTNET_API_KEY_4"]

    def secret(self):
        creds = credentials.decoded_credentials
        if self == Account.one:
            return creds["PHEMEX_API_SECRET_1"]
        elif self == Account.two:
            return creds["PHEMEX_API_SECRET_2"]
        elif self == Account.three:
            return creds["PHEMEX_API_SECRET_3"]
        elif self == Account.four:
            return creds["PHEMEX_API_SECRET_4"]
        elif self == Account.test_one:
            return creds["PHEMEX_TESTNET_API_SECRET_1"]
        elif self == Account.test_two:
            return creds["PHEMEX_TESTNET_API_SECRET_2"]
        elif self == Account.test_three:
            return creds["PHEMEX_TESTNET_API_SECRET_3"]
        elif self == Account.test_four:
            return creds["PHEMEX_TESTNET_API_SECRET_4"]

    def strategy(self):
        if self == Account.one or self == Account.test_one:
            return "strategy_one"
        elif self == Account.two or self == Account.test_two:
            return "strategy_two"
        elif self == Account.three or self == Account.test_three:
            return "strategy_three"
        elif self == Account.four or self == Account.test_four:
            return "strategy_four"

    def data(self):
        if self == Account.one or self == Account.test_one:
            return "fifteen_minute_data"
        elif self == Account.two or self == Account.test_two or self == Account.three or self == Account.test_three:
            return "five_minute_data"
        elif self == Account.four or self == Account.test_four:
            return "one_hour_data"

    def name(self):
        if self.strategy() == "strategy_one":
            return "Classic"
        elif self.strategy() == "strategy_two":
            return "Scalper"
        elif self.strategy() == "strategy_three":
            return "Engulfer"
        elif self.strategy() == "strategy_four":
            return "The Works"


