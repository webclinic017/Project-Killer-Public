# Verdict.py

import enum


def contract_holdings(api):
    current_balance = api.current_balance()
    return float(current_balance['accountBalance']) - float(current_balance['totalUsedBalance'])


class Verdict(enum.Enum):
    long = "long"
    short = "short"
    long_sell = "long_sell"
    short_sell = "short_sell"
    long_buy = "long_buy"
    short_buy = "short_buy"
    put = "put"

    def is_long_type(self):
        if self == Verdict.long or self == Verdict.long_sell or self == Verdict.long_buy:
            return True
        return False

    def is_buy_type(self):
        if self == Verdict.long or self == Verdict.long_buy or self == Verdict.short_buy:
            return True
        return False

    def is_simple_type(self):
        if self == Verdict.short_buy or self == Verdict.short_sell or self == Verdict.long_buy or self == Verdict.long_sell:
            return True
        return False

    def name(self):
        if self.is_long_type():
            return "Long"
        else:
            return "Short"

    def side(self, api):
        if self.is_buy_type():
            return api.Side.buy.value
        else:
            return api.Side.sell.value

    def get_params_for_order(self, price, account, latest_entry, current_time, fraction_to_use, ticker, api):
        info_dict_build = {
            "symbol": ticker,
            "ordType": api.OrderType.market.value,
            "timeInForce": api.TimeInForce.fill_or_kill.value,
            "priceEp": price * 10000,
            "side": self.side(api),
            "takeProfitEp": None,
            "tpTrigger": api.TriggerType.by_last_price.value,
            "stopLossEp": None,
            "slTrigger": api.TriggerType.by_last_price.value
        }

        if self == Verdict.long:
            info_dict_build.update({
                "takeProfitEp": account.upper_limit(price, self, latest_entry) * 10000,
                "stopLossEp": account.lower_limit(price, self, latest_entry) * 10000,
            })
        elif self == Verdict.short:
            info_dict_build.update({
                "takeProfitEp": account.lower_limit(price, self, latest_entry) * 10000,
                "stopLossEp": account.upper_limit(price, self, latest_entry) * 10000
            })

        qty = None
        cl_ord_id = f"{info_dict_build['side'].lower()} {str(current_time)}"
        if self.is_simple_type():
            cl_ord_id += f" {self.name()}"
            position = api.query_open_positions(ticker)[0]
            qty = position["orderQty"]
        else:
            qty = contract_holdings(api) * fraction_to_use

        info_dict_build.update({
            "clOrdID": cl_ord_id,
            "orderQty": qty,
        })

        return info_dict_build

