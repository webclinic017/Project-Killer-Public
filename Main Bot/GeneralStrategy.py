import math

from Account import Account
import phemex
import firebase as ref
import datetime
import requests
from Verdict import Verdict
import time
import boto3
import json

Mock = ref.get_data("Mock").json()
api: phemex.Client = phemex.Client()


def get_current_price(ticker):
    global api
    temp_account = api.account
    account = Account.one
    if Mock:
        account = Account.test_one
    api.update_client(account, Mock)
    close_price = api.query_24h_ticker(ticker)["result"]["markPrice"]
    api.update_client(temp_account, Mock)
    return close_price / 10000


def has_existing_order(account, ticker):
    global api
    temp_account = api.account
    api.update_client(account, Mock)
    orders = api.query_open_orders(ticker)
    api.update_client(temp_account, Mock)
    if orders:
        return True
    return False


def get_existing_orders(account, ticker):
    global api
    temp_account = api.account
    api.update_client(account, Mock)
    orders = api.query_open_orders(ticker)
    api.update_client(temp_account, Mock)
    return orders


def upload_data(path, data):
    data_to_upload = {}
    for i in data:
        data_to_upload[str(i).lower()] = data[i][-1]

    data_to_upload['time'] = str(datetime.datetime.utcfromtimestamp(data_to_upload['time']).isoformat(timespec='seconds')) + 'Z'
    ref.update_firebase(path, data_to_upload)


def send_notification(title, body):
    url = "https://awj5pj35ii.execute-api.us-east-2.amazonaws.com/send_notification"
    params = {
        "title": title,
        "body": body,
        "token": ref.get_data("token").json()
    }
    requests.post(url, params=params)


def validate_order(verdict, current_time, account, fraction_to_use, ticker):
    latest_entry = ref.get_data(f"{ticker.replace('USD', '')}/data/{account.data()}/{str(current_time)}").json()
    print("latest entry")
    print(latest_entry)

    current_price = get_current_price(ticker)
    params = verdict.get_params_for_order(current_price, account, latest_entry, current_time, fraction_to_use, ticker, api)
    print("params")
    print(params)
    print("Current Price: " + str(current_price))

    if params["takeProfitEp"] and abs(params["priceEp"] - params["takeProfitEp"]) <= (params["priceEp"] * 0.0015 * 1.2):
        # checks minimum profit threshold based on fee rate @ 2 * 0.075%
        print("Aborting Order: Take profit levels not exceeding fee rate")
        return True

    params["priceEp"] = None
    order = api.place_order(params)
    if "code" in order and order["code"] == 0:
        order_data = order["data"]
        order_id = order_data["orderID"]
        check_order = api.get_order_by_id(ticker, [order_id])
        if "code" in check_order and check_order["code"] == 0:
            while not check_order["data"]:
                check_order = api.get_order_by_id(ticker, [order_id])
                time.sleep(0.01)

            status = check_order["data"][0]["ordStatus"]
            print("Order " + status)
            if status == api.OrderStatus.canceled.value:
                return validate_order(verdict, current_time, account, fraction_to_use, ticker)
            else:
                if verdict.is_simple_type():
                    executed_price = api.get_executed_price(ticker, order_id)
                    if verdict.is_buy_type():
                        ref.update_firebase(
                            f"{ticker.replace('USD', '')}/bots/{account.strategy()}/verdict_ids/{str(current_time)}",
                            {"market": order_id})
                        send_notification(
                            f"{account.name()} ({ticker.replace('USD', '')}): {verdict.name()}",
                            f"Price: {format_number(executed_price)}")
                    else:
                        closed_price = executed_price
                        order = check_order["data"][0]
                        timestamp = datetime.datetime.fromtimestamp(order['actionTimeNs'] / 1000000000)
                        formatted_timestamp = timestamp.strftime('%m-%d-%Y %H:%M:%S')
                        val = order["cumValueEv"] / 100000000
                        fee_rate = 0.0015  # 0.15 %
                        pnl = (order['closedPnlEv'] / 10000) - (val * ((closed_price + executed_price) / 2) * fee_rate)
                        send_notification(
                            f"{account.name()} ({ticker.replace('USD', '')}): Order Complete",
                            f"Filled at {str(formatted_timestamp)} for ${str(closed_price)}\nPNL: ${str(pnl)}")
                        ref.update_firebase(f"{ticker.replace('USD', '')}/orders/{account.strategy()}/{order_id}", order)
                else:
                    new_params = change_and_post_order(account, order_id, int(current_time), ticker, verdict, latest_entry)
                    title = f"{account.name()} ({ticker.replace('USD', '')}): {verdict.name()}"
                    body = f"Price: {format_number(new_params['price'])}\nTake Profit: {format_number(new_params['takeProfitEp'] / 10000)}\nStop Loss: {format_number(new_params['stopLossEp'] / 10000)}"
                    send_notification(title, body)
                    print("Order Updated")

    return False


def change_and_post_order(account, market_id, current_time, ticker, verdict, latest_entry):
    executed_price = api.get_executed_price(ticker, market_id)
    params = {"price": executed_price}
    if verdict == Verdict.long:
        params["stopLossEp"] = account.lower_limit(executed_price, verdict, latest_entry) * 10000
        params["takeProfitEp"] = account.upper_limit(executed_price, verdict, latest_entry) * 10000
    elif verdict == Verdict.short:
        params["stopLossEp"] = account.upper_limit(executed_price, verdict, latest_entry) * 10000
        params["takeProfitEp"] = account.lower_limit(executed_price, verdict, latest_entry) * 10000

    all_orders = api.query_open_orders(ticker)
    collect_ids = {"market": market_id}
    for i in all_orders:
        tim = int(i['actionTimeNs'] / 1000000000)
        status = i['ordStatus']
        symbol = i["symbol"]
        if (int(current_time) - 10 < tim < int(
                current_time) + 10) and status != api.OrderStatus.canceled.value and symbol == ticker:
            new_id = i['orderID']
            order_type = i["orderType"]
            if order_type == api.OrderType.stop.value:
                collect_ids["stop"] = new_id
                new_params = {
                    "stopPxEp": int(params["stopLossEp"])
                }
                api.amend_order(ticker, new_id, new_params)
            elif order_type == api.OrderType.market_if_touched.value:
                collect_ids["profit"] = new_id
                new_params = {
                    "stopPxEp": int(params["takeProfitEp"])
                }
                api.amend_order(ticker, new_id, new_params)

    ref.update_firebase(f"{ticker.replace('USD', '')}/bots/{account.strategy()}/verdict_ids/{str(current_time)}", collect_ids)

    return params


def format_number(num):
    if num > 1000:
        return str(int(num))
    num = num * 1000
    num = int(num)
    num = float(num) / 1000
    return str(num)


def get_polarity(account, ticker):
    polarity = ref.get_data(ticker + "/bots/" + account.strategy() + "/polarity").json()
    if polarity is None:
        polarity = True
        ref.update_firebase(ticker + "/bots/" + account.strategy() + "/polarity", polarity)
    return ref.get_data(ticker + "/bots/" + account.strategy() + "/polarity").json()


def log_potential_order(ticker, use_api, strategy):
    if use_api:
        url = "https://2aghx2t2kd.execute-api.us-east-2.amazonaws.com"
        params = {
            "currency": ticker,
            "strategy": strategy
        }
        requests.post(url, params=params)
    else:
        client = boto3.client("sqs")
        params = {
            "currency": ticker,
            "strategy": strategy
        }
        client.send_message(
            QueueUrl="https://sqs.us-east-2.amazonaws.com/740338598261/Log_Order_Queue",
            MessageBody=json.dumps(params)
        )

