# StrategyThree.py
# Copyright Yush Raj Kapoor
# Created 03/13/2022

import GeneralStrategy
from Verdict import Verdict
from Account import Account
import time


def account():
    if GeneralStrategy.Mock:
        return Account.test_three
    return Account.three


class StrategyThree:
    def __init__(self, data, ticker):
        self.ema200 = data["Ema200"]
        self.rsi = data["RSI"]
        self.engulfing = data["Engulfing"]
        self.price = data["Price"]
        self.low = data["Low"]
        self.high = data["High"]
        self.std = data["Std"]
        self.time = data["Time"]
        self.ticker = ticker

    @property
    def decide(self):
        print("Making Strategy Three Decision")
        ema200_value = self.ema200[-1]
        rsi_value = self.rsi[-1]
        price_value = self.price[-1]
        engulfing_value = self.engulfing[-1]
        low_value = self.low[-1]
        high_value = self.high[-1]

        fee_total = 0.15  # (0.075 * 2)%
        rsi_long = rsi_value > 50
        ema_long = price_value > ema200_value
        engulfing_long = engulfing_value == "Bullish"
        delta_long = abs(high_value - price_value) >= (price_value * fee_total)
        rsi_short = rsi_value < 50
        ema_short = price_value < ema200_value
        engulfing_short = engulfing_value == "Bearish"
        delta_short = abs(price_value - low_value) >= (price_value * fee_total)

        verdict = Verdict.put
        polarity = GeneralStrategy.get_polarity(account(), self.ticker)

        if rsi_long and ema_long and engulfing_long:
            # Verdict: BUY
            if polarity:
                verdict = Verdict.long
            else:
                verdict = Verdict.short
        elif rsi_short and ema_short and engulfing_short:
            # Verdict: SELL
            if polarity:
                verdict = Verdict.short
            else:
                verdict = Verdict.long

        return verdict

    def account(self):
        return account()
