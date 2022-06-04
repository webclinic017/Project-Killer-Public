# StrategyFive.py
# Copyright Yush Raj Kapoor
# Created 03/29/2022

import GeneralStrategy
from Verdict import Verdict
from Account import Account


class StrategyFive:
    def __init__(self, data, current_time, ticker):
        self.bollinger_upper = data["Bollinger_High"]
        self.bollinger_middle = data["Bollinger_Middle"]
        self.bollinger_lower = data["Bollinger_Low"]
        self.bollinger_validation = data["Bollinger_Validation"]
        self.close = data["Close"]
        self.ticker = ticker + "USD"
        self.current_time = current_time

    @property
    def decide(self):
        print("Making Strategy Five Decision")

        bollinger_upper_value = self.bollinger_upper[-1]
        bollinger_middle_value = self.bollinger_middle[-1]
        bollinger_lower_value = self.bollinger_lower[-1]
        bollinger_validation_value = self.bollinger_validation[-1]
        close_value = self.close[-1]

        verdict = Verdict.put
        polarity = GeneralStrategy.get_polarity(self.account(), self.ticker.replace("USD", ""))
        positions = GeneralStrategy.api.query_open_positions(self.ticker)

        if positions:
            first = positions[0]
            if "long" in first["clOrdID"].lower() and close_value < bollinger_middle_value:
                if polarity:
                    verdict = Verdict.long_sell
                else:
                    verdict = Verdict.short_sell
            elif "short" in first["clOrdID"].lower() and close_value > bollinger_middle_value:
                if polarity:
                    verdict = Verdict.short_sell
                else:
                    verdict = Verdict.long_sell
        else:
            if bollinger_validation_value:
                if close_value > bollinger_upper_value:
                    if polarity:
                        verdict = Verdict.long_buy
                    else:
                        verdict = Verdict.short_buy
                if close_value < bollinger_lower_value:
                    if polarity:
                        verdict = Verdict.short_buy
                    else:
                        verdict = Verdict.long_buy
        return verdict

    def account(self):
        if GeneralStrategy.Mock:
            return Account.test_five
        return Account.five






