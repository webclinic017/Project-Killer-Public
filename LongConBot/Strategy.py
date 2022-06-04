# StrategyOne.py
# Copyright Yush Raj Kapoor
# Created 02/09/2022
import datetime

import pandas as pd

from Verdict import Verdict
from Account import Account


class Strategy:
    def __init__(self, df):
        self.fng = df["fng"]
        self.sma = df["sma730"]
        self.puell = df["puell"]
        self.price = df["price"]

    @property
    def decide(self):
        print("Making Decision")

        verdict = Verdict.put

        if self.fng <= 20 and self.puell <= 0.5 and self.price < self.sma:
            verdict = Verdict.buy
        elif self.fng >= 75 or self.puell >= 4.0 or self.price > self.sma:
            verdict = Verdict.sell

        return verdict

    def account(self):
        return Account.paper1


