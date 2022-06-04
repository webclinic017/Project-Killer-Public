# LongConBot.py
# Copyright Yush Raj Kapoor
# Created 03/29/2022

import datetime
import time
import alpaca_trade_api
import pandas as pd
import pandas_ta as ta
import requests
from Account import Account
from GeneralStrategy import (get_buy_price, get_sell_price, get_coins_and_usd)
from Strategy import Strategy
from Verdict import Verdict
import firebase as ref

Mock = True
Ticker = "BTCUSD"

alpaca: alpaca_trade_api.REST = None
buy_price = get_buy_price()
sell_price = get_sell_price()


def validate_prices():
    # I witnessed a major glitch where the buy/sell price went haywire
    average = (buy_price + sell_price) / 2
    if ((buy_price / average) - 1) > 1 or ((average / sell_price) - 1) > 1:
        return False

    return True


def perform_action_with(action, account, current_time):
    coins, available_usd = get_coins_and_usd(account)
    strategy = account.strategy()
    validation = validate_prices()

    if action == Verdict.buy and float(coins) < 0.001 and validation:
        buy(available_usd)
        send_notification("LongConBot is Active!!", "LongConBot has completed a BUY order! How Exciting!")
    elif action == Verdict.sell and float(coins) > 0.0 and validation:
        sell(coins)
        send_notification("LongConBot is Active!!", "LongConBot has completed a SELL order! How Exciting!")
    else:
        print("\tNo Action Required")


def get_data():
    daily_data = consolidate_data(1440)
    current_time = str(int(time.time()))

    strat = Strategy(daily_data)
    action = strat.decide
    perform_action_with(action, Account.paper1, current_time)

    print("Script Completed. Fuck you.")


def consolidate_data(period):
    bars = get_bars(period_days=1500, interval_days=period)
    df = pd.DataFrame(data=bars)
    close = df['c']

    multiple = float(get_puell_multiple().json())
    sma730 = ta.sma(close, length=730)
    last_sma730 = sma730[len(sma730) - 1]
    fng = int(get_fng_index())
    price = close[len(close) - 1]

    data = {
        "puell": multiple,
        "sma730": last_sma730,
        "fng": fng,
        "price": price
    }
    return data


def get_puell_multiple():
    url = "https://puell-multiple-92357-default-rtdb.firebaseio.com/puell.json"
    headers = {'content-type': 'application/json; charset=UTF-8'}
    data = requests.get(url, headers=headers)
    return data


def get_fng_index():
    url = "https://api.alternative.me/fng/"
    response = requests.get(url)
    value = response.json()["data"][0]["value"]
    return value


def get_bars(period_days, interval_days):
    rest = alpaca_trade_api.rest
    now = time.time()
    days_ago = period_days * 24 * 60 * 60
    delta = now - days_ago
    formatted_start = str(datetime.datetime.utcfromtimestamp(delta).isoformat(timespec='seconds')) + 'Z'
    formatted_now = str(datetime.datetime.utcnow().isoformat(timespec='seconds')) + 'Z'

    bars = alpaca.get_bars("BTCUSD", timeframe=rest.TimeFrame(1, rest.TimeFrameUnit.Day),
                           start=formatted_start, end=formatted_now, market_type=rest.MarketType.crypto, limit=10000)
    return bars


def set_alpaca_account(account):
    global alpaca
    alpaca = account.alpaca_account()
    
    
def send_notification(title, body):
    url = "https://awj5pj35ii.execute-api.us-east-2.amazonaws.com/send_notification"
    params = {
        "title": title,
        "body": body,
        "token": ref.get_data("token").json()
    }
    requests.post(url, params=params)


def buy(cash):
    print("Action -> BUY")

    response = alpaca.submit_order(
        symbol=Ticker,
        notional=cash,
        side="buy",
        type="market",
        time_in_force='fok'
    )

    if response.__getattr__('failed_at') is not None:
        buy(cash)


def sell(coins):
    print("Action -> SELL")

    response = alpaca.submit_order(
        symbol=Ticker,
        qty=coins,
        side="sell",
        type="market",
        time_in_force='fok'
    )

    if response.__getattr__('failed_at') is not None:
        sell(coins)


def start():
    global alpaca
    if Mock:
        set_alpaca_account(Account.paper1)
    else:
        set_alpaca_account(Account.real)

    get_data()


def lambda_handler(event, context):
    print("Starting Long Con Ignition")
    start()
    return "Hello World"


if __name__ == '__main__':
    lambda_handler(None, None)
