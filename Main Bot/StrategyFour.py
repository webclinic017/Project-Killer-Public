# StrategyFour.py
# Copyright Yush Raj Kapoor
# Created 03/20/2022


import GeneralStrategy
from Verdict import Verdict
from Account import Account
import firebase as ref


def account():
    if GeneralStrategy.Mock:
        return Account.test_four
    return Account.four


class StrategyFour:
    def __init__(self, data, current_time, ticker):
        self.tsv = data["TSV"]
        self.ema200 = data["Ema200"]
        self.s_trend_direction10 = data["Supertrend_Direction10"]
        self.s_trend_direction11 = data["Supertrend_Direction11"]
        self.s_trend_direction12 = data["Supertrend_Direction12"]
        self.s_trend_value10 = data["Supertrend_Value10"]
        self.s_trend_value11 = data["Supertrend_Value11"]
        self.s_trend_value12 = data["Supertrend_Value12"]
        self.k_data = data["K_Data"]
        self.d_data = data["D_Data"]
        self.price = data["Price"]
        self.high = data["High"]
        self.low = data["Low"]
        self.current_time = current_time
        self.ticker = ticker

    @property
    def decide(self):
        print("Making Strategy Four Decision")

        if self.actual_order():
            return Verdict.put

        tsv_value = self.tsv[-1]
        ema200_value = self.ema200[-1]
        k_value = self.k_data[-1]
        d_value = self.d_data[-1]
        s_trend10_direction = self.s_trend_direction10[-1]
        s_trend11_direction = self.s_trend_direction11[-1]
        s_trend12_direction = self.s_trend_direction12[-1]
        price_value = self.price[-1]

        verdict = Verdict.put

        trends = [s_trend10_direction, s_trend11_direction, s_trend12_direction]
        above_count = 0
        below_count = 0
        for i in trends:
            if i > 0:
                above_count += 1
            elif i < 0:
                below_count += 1

        tsv_long = tsv_value > 0
        ema200_long = price_value > ema200_value
        stoch_rsi_long = (k_value < 20 or d_value < 20) and (k_value < 80 or d_value < 80)
        trend_long = above_count >= 2
        tsv_short = tsv_value < 0
        ema200_short = price_value < ema200_value
        stoch_rsi_short = (k_value > 80 or d_value > 80) and (k_value > 20, d_value > 20)
        trend_short = below_count >= 2

        polarity = GeneralStrategy.get_polarity(account(), self.ticker)
        if tsv_long and ema200_long and stoch_rsi_long and trend_long:
            if polarity:
                verdict = Verdict.long
            else:
                verdict = Verdict.short
        elif tsv_short and ema200_short and stoch_rsi_short and trend_short:
            if polarity:
                verdict = Verdict.short
            else:
                verdict = Verdict.long

        self.pseudo_order(verdict)

        return verdict

    def pseudo_order(self, verdict):
        s_trend10_value = self.s_trend_value10[-1]
        s_trend11_value = self.s_trend_value11[-1]
        s_trend12_value = self.s_trend_value12[-1]
        price_value = self.price[-1]
        if verdict == Verdict.long:
            stop_loss = price_value - max(price_value - s_trend10_value, price_value - s_trend11_value, price_value - s_trend12_value)
            take_profit = (price_value + (price_value - stop_loss))
            json = {
                "time": self.current_time,
                "type": "long",
                "price": price_value,
                "take_profit": take_profit,
                "stop_loss": stop_loss,
                "triggered": False
            }
            ref.update_firebase(self.ticker + "/pseudo/strategy_four/" + str(self.current_time), json)
        elif verdict == Verdict.short:
            stop_loss = price_value + max(s_trend10_value - price_value, s_trend11_value - price_value, s_trend12_value - price_value)
            take_profit = (price_value - (stop_loss - price_value))
            json = {
                "time": self.current_time,
                "type": "short",
                "price": price_value,
                "take_profit": take_profit,
                "stop_loss": stop_loss,
                "triggered": False
            }
            ref.update_firebase(self.ticker + "/pseudo/strategy_four/" + str(self.current_time), json)

    def actual_order(self):
        api = GeneralStrategy.api.update_client(account(), GeneralStrategy.Mock)
        data = ref.get_data(self.ticker + "/pseudo/strategy_four").json()
        if not data:
            data = []
        reference_order = {}

        has_existing_order = GeneralStrategy.has_existing_order(account(), self.ticker + "USD")
        for i in data:
            triggered = data[i]["triggered"]
            if not triggered:
                if not has_existing_order:
                    ref.update_firebase(self.ticker + "/pseudo/strategy_four/" + data[i]["time"] + "/triggered", True)
                    continue
                reference_order = data[i]
                continue

        if len(reference_order) != 0:
            tm = reference_order["time"]
            order_ids = ref.get_data(self.ticker + "/bots/strategy_four/verdict_ids/" + tm).json()
            if order_ids and len(order_ids) == 0:
                GeneralStrategy.send_notification("ERROR STRATEGY FOUR", "Function: actual_order()\nTimestamp: " + tm + "\nDescription: entry not found in bots/strategy_four/verdict_ids/")

            tp = reference_order["type"]
            requires_amendment = False
            high_value = self.high[-1]
            low_value = self.low[-1]
            stop_loss = reference_order["price"]
            if tp == "long" and high_value >= reference_order["take_profit"]:
                requires_amendment = True
            elif tp == "short" and low_value <= reference_order["take_profit"]:
                requires_amendment = True

            if requires_amendment:
                api.amend_order(self.ticker, order_ids["stop"], params={"stopLossEp": int(stop_loss * 10000)})
                ref.update_firebase(self.ticker + "/pseudo/strategy_four/" + tm + "/triggered", True)
                GeneralStrategy.send_notification("The Works: Amendment Complete", "Stop Loss: " + stop_loss)
                return True

        return False

    def account(self):
        return account()


