# main.py
# Created 05/05/2022
# Copyright Yush Raj Kapoor

import json
import requests
import firebase as ref
import phemex
from Account import Account
import IntervalData
import Finnhub
import time
import threading
import boto3

Mock = ref.get_data("Mock").json()
api: phemex.Client = phemex.Client()
sqs_client = boto3.client("sqs")
data_intervals = [5, 15, 60]
is_aws = True


def begin(currency):
    set_phemex_account(Account.one)
    currency_coin_pairs = ref.get_data("currency_coin_pairs").json()
    aggregate_data = {}

    threads_1 = []
    threads_2 = []
    for minute_interval in data_intervals:
        t1 = threading.Thread(target=retrieve_data,
                              args=(minute_interval, aggregate_data, currency, currency_coin_pairs))
        t2 = threading.Thread(target=handle_data, args=(minute_interval, aggregate_data, currency))
        threads_1.append(t1)
        threads_2.append(t2)

    for thread in threads_1:
        thread.start()

    while True:
        p1 = True
        p2 = True
        for minute_interval in data_intervals:
            if minute_interval not in aggregate_data or len(aggregate_data) != len(data_intervals):
                p1 = False
                continue
            if minute_interval not in aggregate_data or len(aggregate_data[minute_interval]) == 0:
                p2 = False
        if p1 and p2:
            break
        time.sleep(0.1)

    for thread in threads_2:
        thread.start()

    while True:
        p1 = True
        for interval in aggregate_data:
            if aggregate_data[interval] is not None:
                p1 = False
        if p1:
            break
        time.sleep(0.1)

    print("These bitches need to learn how to do this themselves.")


def retrieve_data(minute_interval, aggregate_data, code, currency_coin_pairs):
    aggregate_data.update({minute_interval: {}})
    candle = {}
    if code in currency_coin_pairs:
        candle = Finnhub.get_bars(code + currency_coin_pairs[code], minute_interval)
    else:
        gear = 0
        loop_timeout = 10
        while 's' not in candle or candle['s'] != "ok":
            if loop_timeout <= 0:
                break
            if gear == 0:
                candle = Finnhub.get_bars(code + "USDC", minute_interval)
                gear = 1
            elif gear == 1:
                candle = Finnhub.get_bars(code + "USDT", minute_interval)
                gear = 0
                loop_timeout -= 1

        if gear == 0:
            ref.update_firebase("currency_coin_pairs/" + code, "USDT")
        elif gear == 1:
            ref.update_firebase("currency_coin_pairs/" + code, "USDC")

    print(code + ": Data retrieved at a " + str(minute_interval) + " minute interval")
    candle = format_candle(candle, code)
    aggregate_data[minute_interval].update({0: candle})


def handle_data(minute_interval, aggregate_data, currency):
    currency_snapshot = ref.get_data("rolling_aggregate_data/" + str(minute_interval) + "/" + currency).json()
    interval_data = IntervalData.get_interval_data(minute_interval)
    time_threshold = int(time.time()) - (interval_data.deletion_limit() * minute_interval * 60 * 1.03)
    amalgamated_data = {}
    force_initial = False
    if currency_snapshot is None or currency_snapshot["Time"][0] < time_threshold or force_initial:
        # if asset is new or hasn't been updated correctly
        print(currency + " is a new asset or hasn't been updated in a while, a full data retrieval is underway")
        candles = {}
        gear = 0
        while 's' not in candles or candles['s'] != "ok":
            if gear == 0:
                candles = Finnhub.get_full_bars(interval_data.period_days(), interval_data.value,
                                                str(currency) + "USDC")
                gear = 1
            elif gear == 1:
                candles = Finnhub.get_full_bars(interval_data.period_days(), interval_data.value,
                                                str(currency) + "USDT")
                gear = 0

        print(currency + ": Full Data retrieved at a " + str(minute_interval) + " minute interval")
        candles = format_initial_candles(candles)
        amalgamated_data = interval_data.add_ta(candles, is_initial=True)
    else:
        blank = interval_data.blank_data()
        new_currency_data = aggregate_data[minute_interval][0]
        old_currency_data = currency_snapshot
        if not interval_data.is_correct_format(old_currency_data):
            old_currency_data = blank
        amalgamated_data = interval_data.merge_data(old_currency_data, new_currency_data)
        amalgamated_data = interval_data.add_ta(amalgamated_data)
        while len(amalgamated_data['Close']) > interval_data.deletion_limit():
            amalgamated_data = interval_data.delete_first(amalgamated_data)

    ref.update_firebase("rolling_aggregate_data/" + str(minute_interval) + "/" + str(currency),
                        data_for_database(amalgamated_data))
    print(str(currency) + ": " + str(minute_interval) + " Minute Data Recorded")
    make_decision(currency, str(minute_interval), data_for_decision(amalgamated_data, minute_interval))
    print("Decision called for " + str(currency) + " – " + str(minute_interval) + " Minute Interval")
    aggregate_data[minute_interval] = None


def data_for_decision(data, data_interval):
    if data_interval == 5:
        for i in data:
            data[i] = data[i][-25:]
    if data_interval == 15:
        for i in data:
            data[i] = data[i][-12:]
    elif data_interval == 60:
        for i in data:
            data[i] = [data[i][-1]]
    for i in data:
        for j in data[i]:
            if str(j) == "nan":
                print("Error " + i)

    return data


def data_for_database(data):
    new_data = {}
    for i in IntervalData.default_directory():
        new_data[i] = data[i]

    return new_data


def make_decision(symbol, data_interval, data):
    if is_aws:
        params = {
            "symbol": symbol,
            "data_interval": data_interval,
            "data": data
        }
        sqs_client.send_message(
            QueueUrl="https://sqs.us-east-2.amazonaws.com/740338598261/Main_Bot_Queue",
            MessageBody=json.dumps(params)
        )
    else:
        url = "https://utvxor4hzd.execute-api.us-east-2.amazonaws.com/run"
        params = {
            "symbol": symbol,
            "data_interval": data_interval,
            "data": json.dumps(data)
        }
        requests.post(url, params=params)


def format_candle(candle, currency):
    directory = {'c': "Close", 'h': "High", 'l': "Low", 'o': "Open", 't': "Time", 'v': "Volume"}
    new_candle = {}
    for i in directory:
        new_candle[directory[i]] = candle[i][0]
    new_candle["Price"] = get_market_price(str(currency) + "USD")
    return new_candle


def format_initial_candles(candles):
    directory = {'c': "Close", 'h': "High", 'l': "Low", 'o': "Open", 't': "Time", 'v': "Volume"}
    new_candles = {}
    for i in directory:
        new_candles[directory[i]] = candles[i]
    return new_candles


def get_market_price(symbol):
    index_price = api.query_24h_ticker(symbol)["result"]["markPrice"]
    return index_price / 10000


def set_phemex_account(account):
   api.update_client(account.key(), account.secret(), Mock)


def validate(event):
    active_currencies = ref.get_data("active_currencies").json()

    if "Records" in event:
        sub_records = event["Records"]
        if type(sub_records) == list:
            records = sub_records[0]
            if "body" in records:
                params = json.loads(records["body"])
                if "symbol" not in params:
                    return {'statusCode': 405, 'body': json.dumps("Validation Error: 'symbol' parameter not found")}
                else:
                    sym = params["symbol"]
                    if sym not in active_currencies:
                        return {'statusCode': 405, 'body': json.dumps("Validation Error: Value for 'symbol' is invalid")}
        else:
            return {'statusCode': 405, 'body': json.dumps("Validation Error: key 'body' does not exist")}
    elif "rawQueryString" in event:
        return None
    else:
        return {'statusCode': 405, 'body': json.dumps("Validation Error: key 'Records' does not exist")}


def lambda_handler(event, context):
    print("Starting")
    if context == "not_aws":
        global is_aws
        is_aws = False

    validation = validate(event)
    if validation is None:
        print("Validation Complete")
        json_obj = None
        if "queryStringParameters" in event:
            event["queryStringParameters"]["data"] = json.loads(event["queryStringParameters"]["data"])
            json_obj = event["queryStringParameters"]
        else:
            json_obj = json.loads(event['Records'][0]['body'])
        currency = json_obj["symbol"]
        begin(currency)
        print("Complete")
        return {'statusCode': 200, 'body': json.dumps("Hello World!")}
    else:
        print(validation["body"])
        return validation


if __name__ == '__main__':
    evt = {
        "Records": [{
            "body": '{"symbol": "AVAX"}'
        }]
    }
    lambda_handler(evt, "not_aws")
