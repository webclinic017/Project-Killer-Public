# StrategyTwo.py
# Copyright Yush Raj Kapoor
# Created 02/23/2022

import GeneralStrategy
from Verdict import Verdict
from Account import Account


def account():
    if GeneralStrategy.Mock:
        return Account.test_two
    return Account.two


class StrategyTwo:
    def __init__(self, data, ticker):
        self.ema25 = data["Ema25"]
        self.ema50 = data["Ema50"]
        self.ema100 = data["Ema100"]
        self.price = data["Price"]
        self.range = -25
        self.ticker = ticker

    @property
    def decide(self):
        print("Making Strategy Two Decision")
        ema25_value = self.ema25[-1]
        ema50_value = self.ema50[-1]
        ema100_value = self.ema100[-1]
        price_value = self.price[-1]

        verdict = Verdict.put
        pullback = self.pullback_data()
        crosses = self.crosses(pullback)
        if not crosses:
            return verdict

        first_instance_cross = self.relevant_cross(pullback)
        post_cross_prices = self.price[self.range + first_instance_cross:]
        post_cross_ema25 = self.ema25[self.range + first_instance_cross:]
        post_cross_ema50 = self.ema50[self.range + first_instance_cross:]
        post_cross_ema100 = self.ema100[self.range + first_instance_cross:]

        separation_threshold = price_value * 0.00125
        separation_tier1 = abs(post_cross_ema25[0] - post_cross_ema50[0]) > separation_threshold
        separation_tier2 = abs(post_cross_ema50[0] - post_cross_ema100[0]) > separation_threshold
        separation_tier_main = separation_tier1 and separation_tier2

        tier1_long = price_value >= ema25_value > ema50_value > ema100_value
        tier1_short = price_value <= ema25_value < ema50_value < ema100_value

        abort_long = False
        abort_short = False

        for i in range(len(post_cross_prices)):
            check_cross_price = post_cross_prices[i]
            check_cross_ema100 = post_cross_ema100[i]

            if check_cross_price < check_cross_ema100:
                abort_long = True
            elif check_cross_price >= check_cross_ema100:
                abort_short = True

        polarity = GeneralStrategy.get_polarity(account(), self.ticker)
        if tier1_long and separation_tier_main and not abort_long:
            # Verdict: Buy
            if polarity:
                verdict = Verdict.long
            else:
                verdict = Verdict.short
        elif tier1_short and separation_tier_main and not abort_short:
            # Verdict: Sell
            if polarity:
                verdict = Verdict.short
            else:
                verdict = Verdict.long

        return verdict

    def pullback_data(self):
        last_25_ema25 = self.ema25[self.range:]
        last_25_price = self.price[self.range:]

        pullback = []
        for i in range(len(last_25_price)):
            pullback.append(last_25_price[i] - last_25_ema25[i])

        return pullback

    def crosses(self, pullback_data):
        crosses = False
        positive = False
        negative = False

        for i in pullback_data:
            if i < 0 or negative:
                negative = True
            if i >= 0 or positive:
                positive = True

        if positive and negative:
            crosses = True

        return crosses

    def relevant_cross(self, pullback_data):
        track = None
        indices = []
        for i in range(len(pullback_data)):
            value = pullback_data[i]
            if track is None:
                track = value
            elif (value < 0 and track > 0) or (value > 0 and track < 0):
                indices.append(i)
                track = value

        ind = -1
        if len(indices) > 1:
            ind = -2
        return indices[ind]

    def account(self):
        return account()


