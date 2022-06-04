import hmac
import hashlib
import json
import requests
import time
import enum

from math import trunc
from .exceptions import PhemexAPIException


class Client(object):

    MAIN_NET_API_URL = 'https://api.phemex.com'
    TEST_NET_API_URL = 'https://testnet-api.phemex.com'

    CURRENCY_BTC = "BTC"
    CURRENCY_USD = "USD"

    SYMBOL_BTCUSD = "BTCUSD"
    SYMBOL_ETHUSD = "ETHUSD"
    SYMBOL_XRPUSD = "XRPUSD"

    class Side(enum.Enum):
        buy = "Buy"
        sell = "Sell"

    class TimeInForce(enum.Enum):
        good_till_cancel = "GoodTillCancel"
        immediate_or_cancel = "ImmediateOrCancel"
        fill_or_kill = "FillOrKill"
        post_only = "PostOnly"

    class OrderStatus(enum.Enum):
        new = "New"
        partial_fill = "PartiallyFilled"
        fill = "Filled"
        canceled = "Canceled"
        rejected = "Rejected"
        triggered = "Triggered"
        untriggered = "Untriggered"

    class OrderType(enum.Enum):
        market = "Market"
        limit = "Limit"
        stop = "Stop"
        stop_limit = "StopLimit"
        market_if_touched = "MarketIfTouched"
        limit_if_touched = "LimitIfTouched"

    class TriggerType(enum.Enum):
        by_market_price = "ByMarkPrice"
        by_last_price = "ByLastPrice"

    def __init__(self):
        self.account = None
        self.api_key = None
        self.api_secret = None
        self.api_URL = None
        self.session = requests.session()

    def update_client(self, acct, is_testnet=False):
        self.account = acct
        self.api_key = self.account.key()
        self.api_secret = self.account.secret()
        self.api_URL = self.MAIN_NET_API_URL
        if is_testnet:
            self.api_URL = self.TEST_NET_API_URL

    def _send_request(self, method, endpoint, params={}, body={}):
        expiry = str(trunc(time.time()) + 60)
        query_string = '&'.join(['{}={}'.format(k,v) for k,v in params.items()])
        message = endpoint + query_string + expiry
        body_str = ""
        if body:
            body_str = json.dumps(body, separators=(',', ':'))
            message += body_str
        signature = hmac.new(self.api_secret.encode('utf-8'), message.encode('utf-8'), hashlib.sha256)
        self.session.headers.update({
            'x-phemex-request-signature': signature.hexdigest(),
            'x-phemex-request-expiry': expiry,
            'x-phemex-access-token': self.api_key,
            'Content-Type': 'application/json'})

        url = self.api_URL + endpoint
        if query_string:
            url += '?' + query_string
        response = self.session.request(method, url, data=body_str.encode())
        if response.status_code == 500:
            retry_codes = [39999]
            res_json = response.json()
            if "code" in res_json and res_json["code"] in retry_codes:
                return self._send_request(method, endpoint, params, body)
        if not str(response.status_code).startswith('2'):
            raise PhemexAPIException(response)
        try:
            res_json = response.json()
        except ValueError:
            raise PhemexAPIException('Invalid Response: %s' % response.text)

        ok_codes = [0, 10002, 11055, 11074]
        if "code" in res_json and res_json["code"] not in ok_codes:
            raise PhemexAPIException(response)
        if "error" in res_json and res_json["error"]:
            raise PhemexAPIException(response)
        return res_json

    def conditional_ticker(self, symbol):
        if symbol == "BTCUSD":
            symbol = "uBTCUSD"
        return symbol

    def query_account_n_positions(self, currency: str):
        """
        https://github.com/phemex/phemex-api-docs/blob/master/Public-API-en.md#querytradeaccount
        """
        return self._send_request("get", "/accounts/accountPositions", {'currency': currency})

    def place_order(self, params={}):
        """
        https://github.com/phemex/phemex-api-docs/blob/master/Public-API-en.md#placeorder
        """
        params["symbol"] = self.conditional_ticker(params["symbol"])
        return self._send_request("post", "/orders", body=params)

    def amend_order(self, symbol, orderID, params={}):
        """
        https://github.com/phemex/phemex-api-docs/blob/master/Public-API-en.md#622-amend-order-by-orderid
        """
        symbol = self.conditional_ticker(symbol)
        params["symbol"] = symbol
        params["orderID"] = orderID
        return self._send_request("put", "/orders/replace", params=params)

    def cancel_order(self, symbol, orderID):
        """
        https://github.com/phemex/phemex-api-docs/blob/master/Public-API-en.md#623-cancel-single-order
        """
        return self._send_request("delete", "/orders/cancel", params={"symbol": symbol, "orderID": orderID})

    def _cancel_all(self, symbol, untriggered_order=False):
        """
        https://github.com/phemex/phemex-api-docs/blob/master/Public-API-en.md#625-cancel-all-orders
        """
        return self._send_request("delete", "/orders/all", 
            params={"symbol": symbol, "untriggered": str(untriggered_order).lower()})
    
    def cancel_all_normal_orders(self, symbol):
        self._cancel_all(symbol, untriggered_order=False)

    def cancel_all_untriggered_conditional_orders(self, symbol):
        self._cancel_all(symbol, untriggered_order=True)

    def cancel_all(self, symbol):
        self._cancel_all(symbol, untriggered_order=False)
        self._cancel_all(symbol, untriggered_order=True)

    def change_leverage(self, symbol, leverage=0):
        """
        https://github.com/phemex/phemex-api-docs/blob/master/Public-API-en.md#627-change-leverage
        """
        return self._send_request("PUT", "/positions/leverage", params={"symbol":symbol, "leverage": leverage})

    def change_risklimit(self, symbol, risk_limit=0):
        """
        https://github.com/phemex/phemex-api-docs/blob/master/Public-API-en.md#628-change-position-risklimit
        """
        return self._send_request("PUT", "/positions/riskLimit", params={"symbol":symbol, "riskLimit": risk_limit})

    def query_open_orders(self, symbol):
        """
        https://github.com/phemex/phemex-api-docs/blob/master/Public-API-en.md#6210-query-open-orders-by-symbol
        """
        symbol = self.conditional_ticker(symbol)
        to_return = []
        open_orders = self._send_request("GET", "/orders/activeList", params={"symbol": symbol})
        # For some reason, having the symbol parameter does absolutely fucking nothing but is required...
        if "code" in open_orders and open_orders["code"] == 0:
            if "rows" in open_orders["data"]:
                rows = open_orders["data"]["rows"]
                for row in rows:
                    if row["symbol"] == symbol:
                        to_return.append(row)
        return to_return

    def query_open_positions(self, ticker):
        response = self.get_all_orders(ticker)
        rows = response["data"]["rows"]
        confirmed_open = []
        for row in rows:
            if row["symbol"] == ticker:
                if row["side"] == self.Side.buy.value:
                    confirmed_open.append(row)
                break
        return confirmed_open

    def query_24h_ticker(self, symbol):
        """
        https://github.com/phemex/phemex-api-docs/blob/master/Public-API-en.md#633-query-24-hours-ticker
        """
        symbol = self.conditional_ticker(symbol)
        return self._send_request("GET", "/md/ticker/24hr", params={"symbol": symbol})

    def get_order_by_id(self, symbol, orderIDs):
        symbol = self.conditional_ticker(symbol)
        orderIDs = ",".join(orderIDs)
        return self._send_request("GET", "/exchange/order", params={"symbol": symbol, "orderID": orderIDs})

    def get_all_orders(self, symbol):
        symbol = self.conditional_ticker(symbol)
        return self._send_request("GET", "/exchange/order/list", params={"symbol": symbol, "start": 1600000000000, "end": int(time.time()*1000)})

    def current_balance(self):
        holding = self._send_request("GET", "/phemex-user/users/children", params={})
        thing = holding['data'][0]['userMarginVo']
        for i in thing:
            if i['currency'] == "USD":
                return i
        return {}

    def query_recent_trades(self, symbol):
        symbol = self.conditional_ticker(symbol)
        if symbol == "ETHUSD":
            symbol = "cETHUSD"
        return self._send_request("GET", "/md/trade", params={"symbol": symbol})

    def public_data(self):
        return self._send_request("GET", "/public/products")

    def get_executed_price(self, symbol, order_id):
        start = int(time.time() - 15) * 1000
        end = int(time.time() + 15) * 1000
        symbol = self.conditional_ticker(symbol)
        executed_trades = self._send_request("GET", "/exchange/order/trade", params={"symbol": symbol, "start": start, "end": end})
        if "code" in executed_trades and executed_trades["code"] == 0:
            executed_trades = executed_trades["data"]["rows"]
            for trade in executed_trades:
                if trade["orderID"] == order_id:
                    return float(trade["execPriceEp"] / 10000)

        return None

