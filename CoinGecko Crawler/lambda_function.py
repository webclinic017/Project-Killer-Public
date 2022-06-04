# lambda_function.py

import json
import requests
import firebase as ref
import phemex
import Account
from Coin import Coin

Mock = ref.get_data("Mock").json()
api: phemex.client = phemex.Client()


def gather():
    api.update_client(Account.Account.one, Mock)
    all_currencies = []
    public_info = api.public_info()
    coin_gecko_data = ref.get_data("coin_gecko_data").json()
    if not coin_gecko_data:
        coin_gecko_data = {}

    if "code" in public_info and public_info["code"] == 0:
        currencies = public_info["data"]["products"]
        for i in currencies:
            if "status" in i and i["status"] == "Listed":
                symbol = i["symbol"]
                if symbol[0] != "s" and symbol[0] != "u" and symbol[0] != "c":
                    if symbol[-3:] == "USD":
                        currency = symbol[:-3]
                        all_currencies.append(currency)

    to_remove = []
    for coin in coin_gecko_data:
        if coin not in all_currencies:
            print("Removing Currency: " + coin)
            to_remove.append(coin)

    for i in to_remove:
        coin_gecko_data.pop(i)

    all_url = "https://api.coingecko.com/api/v3/coins/list"
    all_response = requests.get(all_url)
    if "Cloudflare" in all_response.text or all_response.status_code != 200:
        return

    for currency in all_currencies:
        if currency not in coin_gecko_data:
            print("New Currency: " + currency)
            info = get_coin_gecko_info(currency, all_response.json())
            if info:
                coin_gecko_data[info.ticker.upper()] = {
                    "geckoID": info.geckoID,
                    "ticker": info.ticker,
                    "displayName": info.displayName,
                    "marketCap": info.marketCap,
                    "geckoImageURL": info.geckoImageURL
                }
            else:
                print("uh oh " + currency)

    ref.update_firebase("coin_gecko_data", coin_gecko_data)
    print("Completed Caching")


def get_coin_gecko_info(symbol, all_response):
    formatted_symbol = symbol.lower()
    possible_coins = []
    for resp in all_response:
        if resp["symbol"] == formatted_symbol:
            possible_coins.append(resp["id"])

    better_coins = get_market_caps(possible_coins, 1, [])
    if not better_coins:
        return None
    ind = 0
    mx = better_coins[ind]
    while not mx.marketCap:
        ind += 1
        if len(better_coins) < ind:
            mx = better_coins[ind]
        else:
            return None
    for coin in better_coins:
        if coin.marketCap and coin.marketCap > mx.marketCap:
            mx = coin

    return mx


def get_market_caps(gecko_ids, page, new):
    new_coins = new

    url = "https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&ids=" + ",".join(gecko_ids) + "&order=market_cap_desc&per_page=250&page=" + str(page) + "&sparkline=false"
    response = requests.get(url)
    if "Cloudflare" in response.text or response.status_code != 200:
        return None
    jsn = response.json()

    for i in jsn:
        new_coins.append(Coin(i))

    if page <= 10 and len(new_coins) < len(gecko_ids):
        return get_market_caps(gecko_ids, page + 1, new_coins)

    return new_coins


def lambda_handler(event, context):
    print("Starting CoinGecko Crawler")
    gather()


if __name__ == '__main__':
    lambda_handler(None, None)

