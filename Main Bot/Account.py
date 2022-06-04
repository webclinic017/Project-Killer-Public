import enum
import time

import credentials
from Verdict import Verdict


class Account(enum.Enum):
    one = 1
    two = 2
    three = 3
    four = 4
    five = 5
    test_one = 6
    test_two = 7
    test_three = 8
    test_four = 9
    test_five = 10

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
        elif self == Account.five:
            return creds["PHEMEX_API_KEY_5"]
        elif self == Account.test_one:
            return creds["PHEMEX_TESTNET_API_KEY_1"]
        elif self == Account.test_two:
            return creds["PHEMEX_TESTNET_API_KEY_2"]
        elif self == Account.test_three:
            return creds["PHEMEX_TESTNET_API_KEY_3"]
        elif self == Account.test_four:
            return creds["PHEMEX_TESTNET_API_KEY_4"]
        elif self == Account.test_five:
            return creds["PHEMEX_TESTNET_API_KEY_5"]


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
        elif self == Account.five:
            return creds["PHEMEX_API_SECRET_5"]
        elif self == Account.test_one:
            return creds["PHEMEX_TESTNET_API_SECRET_1"]
        elif self == Account.test_two:
            return creds["PHEMEX_TESTNET_API_SECRET_2"]
        elif self == Account.test_three:
            return creds["PHEMEX_TESTNET_API_SECRET_3"]
        elif self == Account.test_four:
            return creds["PHEMEX_TESTNET_API_SECRET_4"]
        elif self == Account.test_five:
            return creds["PHEMEX_TESTNET_API_SECRET_5"]

    def strategy(self):
        if self == Account.one or self == Account.test_one:
            return "strategy_one"
        elif self == Account.two or self == Account.test_two:
            return "strategy_two"
        elif self == Account.three or self == Account.test_three:
            return "strategy_three"
        elif self == Account.four or self == Account.test_four:
            return "strategy_four"
        elif self == Account.five or self == Account.test_five:
            return "strategy_five"

    def data(self):
        if self == Account.one or self == Account.test_one:
            return "fifteen_minute_data"
        elif self == Account.two or self == Account.test_two or self == Account.three or self == Account.test_three:
            return "five_minute_data"
        elif self == Account.four or self == Account.test_four or self == Account.five or self == Account.test_five:
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
        elif self.strategy() == "strategy_five":
            return "BB Squeeze"

    def upper_limit(self, price, verdict, latest_entry):
        if self.strategy() == "strategy_one":
            if verdict == Verdict.long:
                return price * 1.0225
            elif verdict == Verdict.short:
                return price * 1.015

        if self.strategy() == "strategy_two":
            if verdict == Verdict.long:
                lower_limit = self.lower_limit(price, verdict, latest_entry)
                return price + abs(price - lower_limit)
            elif verdict == Verdict.short:
                latest_ema50 = latest_entry["ema50"]
                latest_close = latest_entry["close"]
                if (latest_ema50 - latest_close) < 0:
                    print("WTF Why is EMA50 less than the latest close???")
                return price + (latest_ema50 - latest_close)

        if self.strategy() == "strategy_three":
            if verdict == Verdict.long:
                lower_limit = self.lower_limit(price, verdict, latest_entry)
                return price + abs(price - lower_limit)
            elif verdict == Verdict.short:
                latest_high = latest_entry["high"]
                latest_close = latest_entry["close"]
                return price + (latest_high - latest_close)

        if self.strategy() == "strategy_four":
            if verdict == Verdict.long:
                lower_limit = self.lower_limit(price, verdict, latest_entry)
                return price + ((price - lower_limit) * 2)
            if verdict == Verdict.short:
                supertrend10 = latest_entry["supertrend_value10"]
                supertrend11 = latest_entry["supertrend_value11"]
                supertrend12 = latest_entry["supertrend_value12"]
                return price + max(supertrend10 - price, supertrend11 - price, supertrend12 - price)

        if self.strategy() == "strategy_five":
            return None

    def lower_limit(self, price, verdict, latest_entry):
        if self.strategy() == "strategy_one":
            if verdict == Verdict.long:
                return price * 0.985
            elif verdict == Verdict.short:
                return price * 0.9775

        if self.strategy() == "strategy_two":
            if verdict == Verdict.long:
                latest_ema50 = latest_entry["ema50"]
                latest_close = latest_entry["close"]
                return price - (latest_close - latest_ema50)
            elif verdict == Verdict.short:
                upper_limit = self.upper_limit(price, verdict, latest_entry)
                return price - abs(upper_limit - price)

        if self.strategy() == "strategy_three":
            if verdict == Verdict.long:
                latest_low = latest_entry["low"]
                latest_close = latest_entry["close"]
                return price - (latest_close - latest_low)
            elif verdict == Verdict.short:
                upper_limit = self.upper_limit(price, verdict, latest_entry)
                return price - abs(upper_limit - price)

        if self.strategy() == "strategy_four":
            if verdict == Verdict.long:
                supertrend10 = latest_entry["supertrend_value10"]
                supertrend11 = latest_entry["supertrend_value11"]
                supertrend12 = latest_entry["supertrend_value12"]
                return price - max(price-supertrend10, price-supertrend11, price-supertrend12)
            if verdict == Verdict.short:
                upper_limit = self.upper_limit(price, verdict, latest_entry)
                return price - ((upper_limit - price) * 2)

        if self.strategy() == "strategy_five":
            return None


