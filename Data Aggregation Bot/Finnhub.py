#Finnhub.py
# Copyright Yush Raj Kapoor
# Created 05/05/2022

import finnhub
import credentials
import time

finnhub_api_value = 1


def get_bars(asset, interval_minutes):
    global finnhub_api_value
    creds = credentials.decoded_credentials
    finnhub_client = finnhub.Client(api_key=creds["FINNHUB_API_KEY" + str(finnhub_api_value)])

    interval_seconds = interval_minutes * 60
    five_minute_interval = 5*60
    now = int(int(time.time()) / five_minute_interval) * five_minute_interval

    to = int(time.time())
    if to - now < 60:
        to = now - five_minute_interval

    bars = finnhub_client.crypto_candles('BINANCE:' + asset, interval_minutes, int(now - (2 * interval_seconds) + 1), to)
    if type(bars) is not dict:
        return get_bars(asset, interval_minutes)
    if "Bad Gateway" in bars:
        print("Cloudflare Error: Retrying Data Collection")
        return get_bars(asset, interval_minutes)
    elif 'error' in bars and 'API limit reached' in bars['error']:
        finnhub_api_value += 1
        print("API" + str(finnhub_api_value) + " now active")
        return get_bars(asset, interval_minutes)

    return bars


def get_full_bars(period_days, interval_minutes, asset):
    global finnhub_api_value
    creds = credentials.decoded_credentials
    finnhub_client = finnhub.Client(api_key=creds["FINNHUB_API_KEY" + str(finnhub_api_value)])

    days_ago = period_days * 24 * 60 * 60
    delta = int(time.time() - days_ago)

    five_minute_interval = 5 * 60
    now = int(int(time.time()) / five_minute_interval) * five_minute_interval

    to = int(time.time())
    if to - now < 60:
        delta = delta - five_minute_interval
        to = now - five_minute_interval

    bars = finnhub_client.crypto_candles('BINANCE:' + asset, interval_minutes, delta, to)
    if type(bars) is not dict:
        return get_full_bars(period_days, interval_minutes, asset)
    if "Bad Gateway" in bars:
        print("Cloudflare Error: Retrying Data Collection")
        return get_full_bars(period_days, interval_minutes, asset)
    elif 'error' in bars and 'API limit reached' in bars['error']:
        finnhub_api_value += 1
        print("API" + str(finnhub_api_value) + " now active")
        return get_full_bars(period_days, interval_minutes, asset)
    return bars

