# StrategyOne.py
# Copyright Yush Raj Kapoor
# Created 02/09/2022

import GeneralStrategy
from Verdict import Verdict
from Account import Account


def account():
    if GeneralStrategy.Mock:
        return Account.test_one
    return Account.one


class StrategyOne:
    def __init__(self, data, ticker):
        self.macd = data["Macd"]
        self.signal = data["Signal"]
        self.rsi = data["RSI"]
        self.k_data = data["K_Data"]
        self.d_data = data["D_Data"]
        self.ticker = ticker
        
    @property
    def decide(self):
        print("Making Strategy One Decision")
        k_value = self.k_data[-1]
        d_value = self.d_data[-1]
        rsi_value = self.rsi[-1]
        macd_value = self.macd[-1]
        signal_value = self.signal[-1]

        overbought_level = 80
        oversold_level = 20

        k_check = self.k_data[-12:]
        d_check = self.d_data[-12:]
        k_was_overbought = False
        d_was_overbought = False
        k_was_oversold = False
        d_was_oversold = False
        for i in k_check:
            if i > overbought_level:
                k_was_overbought = True
            if i < oversold_level:
                k_was_oversold = True
        for i in d_check:
            if i > overbought_level:
                d_was_overbought = True
            if i < oversold_level:
                d_was_oversold = True

        k_long = k_was_oversold and k_value < overbought_level
        d_long = d_was_oversold and d_value < overbought_level
        rsi_long = rsi_value > 50
        macd_long = macd_value > signal_value
        k_short = k_was_overbought and k_value > oversold_level
        d_short = d_was_overbought and d_value > oversold_level
        rsi_short = rsi_value < 50
        macd_short = macd_value < signal_value

        verdict = Verdict.put
        polarity = GeneralStrategy.get_polarity(account(), self.ticker)
        if k_long and d_long and rsi_long and macd_long:
            # long position
            if polarity:
                verdict = Verdict.long
            else:
                verdict = Verdict.short
        elif k_short and d_short and rsi_short and macd_short:
            # short position
            if polarity:
                verdict = Verdict.short
            else:
                verdict = Verdict.long

        return verdict

    def account(self):
        return account()

        
