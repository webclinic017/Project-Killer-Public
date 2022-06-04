# main.py
# Created 03/24/2022
# Copyright Yush Raj Kapoor

import time
import firebase as ref
import phemex
import Account
import requests
import datetime
import threading
import boto3
import json

Mock = ref.get_data("Mock").json()
api: phemex.Client = phemex.Client()
sqs_client = boto3.client("sqs")
phemex_safe_block = False
is_aws = True


def begin():
    # TASK 1
    api.update_client(Account.Account.one, Mock)
    active_currencies = ref.get_data("active_currencies").json()
    if not active_currencies:
        return

    blacklist = []
    for code in active_currencies:
        query_24hr = api.query_24h_ticker(str(code) + "USD")

        if "error" in query_24hr and query_24hr["error"] and "code" in query_24hr["error"] and (
                query_24hr["error"]["code"] == 6001 or query_24hr["error"]["code"] == 6003):
            blacklist.append(str(code))

    for i in blacklist:
        if i in active_currencies:
            active_currencies.remove(i)

    results = []
    threads = []
    for currency in active_currencies:
        t = threading.Thread(target=for_each_currency, args=(currency, results))
        threads.append(t)

    for thread in threads:
        thread.start()

    while len(results) != len(active_currencies):
        time.sleep(0.1)


def for_each_currency(currency, results):
    global phemex_safe_block
    strategies = ref.get_data(currency + "/orders").json()
    all_ids = {}
    all_orders = {}
    if strategies is not None:
        for i in strategies:
            strategy = strategies[i]
            all_ids[i] = []
            for j in strategy:
                order = strategy[j]
                if order['ordStatus'] != "Untriggered":
                    all_ids[i].append(order["orderID"])
                    order['strategy'] = i
                    all_orders[order["orderID"]] = order

    print("Database Query for " + currency + " complete")

    # Queries order data from Phemex
    check_all_ids = {}
    check_all_orders = {}
    accounts = Account.all_enums(Mock)
    for account in accounts:
        check_all_ids[account.strategy()] = []
        while phemex_safe_block:
            time.sleep(0.01)
        phemex_safe_block = True
        api.update_client(account, Mock)
        all_orders_phemex = api.get_all_orders(currency + "USD")['data']['rows']
        phemex_safe_block = False
        for order in all_orders_phemex:
            check_all_ids[account.strategy()].append(order['orderID'])
            check_all_orders[order["orderID"]] = order

    print("Phemex Query for " + currency + " complete")

    # Cross checks data between firebase and Phemex to see if there are any new orders
    orders_to_add = {}
    for strategy in check_all_ids.keys():
        orders_to_add[strategy] = []
        for order_id in check_all_ids[strategy]:
            if strategy not in all_ids.keys() or order_id not in all_ids[strategy]:
                orders_to_add[strategy].append(check_all_orders[order_id])

    # These new orders are then added to firebase using their orderID as the key
    for strategy in orders_to_add.keys():
        orders = orders_to_add[strategy]
        for order in orders:
            order['strategy'] = strategy
            all_orders[order['orderID']] = order
            print("Added Order for " + currency)
            ref.update_firebase(currency + "/orders/" + strategy + "/" + str(order['orderID']), order)

    # TASK 2
    # Takes the first snapshot of open orders from firebase
    open_orders_pre = ref.get_data(currency + "/open_orders").json()
    if open_orders_pre is None:
        open_orders_pre = {}

    # finds all open orders using Phemex data and adds them to firebase,
    # regardless of whether they were there before or not
    for strategy in check_all_ids.keys():
        ids = check_all_ids[strategy]
        untriggered_ids = []
        for order_id in ids:
            order = check_all_orders[order_id]
            status = order['ordStatus']
            if status == "Untriggered":
                untriggered_ids.append(order['orderID'])
        ref.update_firebase(currency + "/open_orders/" + strategy, untriggered_ids)

    # The second snapshot of open orders are taken from firebase
    open_orders_post = ref.get_data(currency + "/open_orders").json()
    if open_orders_post is None:
        open_orders_post = {}

    pre_keys = open_orders_pre.keys()
    post_keys = open_orders_post.keys()

    # Cross check between the first and second snapshot to see if open order has been filled
    strategies_order_complete = []
    for i in pre_keys:
        if i not in post_keys:
            strategies_order_complete.append(i)

    # If open order has been filled, then it will query relevant data from Phemex and send a push notification
    for strategy in strategies_order_complete:
        order_ids = open_orders_pre[strategy]
        acc = get_account(strategy, Mock)
        while phemex_safe_block:
            time.sleep(0.01)
        phemex_safe_block = True
        api.update_client(acc, Mock)
        for order_id in order_ids:
            order = api.get_order_by_id(currency + "USD", order_id)['data']
            if len(order) > 0:
                order = order[0]
            else:
                continue
            closed_price = get_executed_price(order_id, currency + "USD")
            executed_price = closed_price

            if order['ordStatus'] != "Deactivated":
                timestamp = datetime.datetime.fromtimestamp(order['actionTimeNs'] / 1000000000)
                formatted_timestamp = timestamp.strftime('%m-%d-%Y %H:%M:%S')
                val = order["cumValueEv"] / 100000000
                fee_rate = 0.0015  # 0.15 %
                pnl = (order['closedPnlEv'] / 10000) - (val * ((closed_price + executed_price) / 2) * fee_rate)
                title = acc.name() + " (" + currency + "): Order Complete"
                body = "Filled at " + str(formatted_timestamp) + " for $" + str(closed_price) + \
                       "\nPNL: $" + str(pnl)
                print("Sent Notification")
                send_notification(title, body)
        phemex_safe_block = False

    start_data_aggregation(currency)
    results.append(currency)


def start_data_aggregation(symbol):
    if is_aws:
        params = {
            "symbol": symbol
        }
        sqs_client.send_message(
            QueueUrl="https://sqs.us-east-2.amazonaws.com/740338598261/Data_Aggregation_Bot_SQS_Queue",
            MessageBody=json.dumps(params)
        )
    else:
        url = "https://exspxqs45l.execute-api.us-east-2.amazonaws.com/Data_Aggregation_Bot"
        params = {
            "symbol": symbol,
        }
        resp = requests.post(url, params=params)


def send_notification(title, body):
    url = "https://awj5pj35ii.execute-api.us-east-2.amazonaws.com/send_notification"
    params = {
        "title": title,
        "body": body,
        "token": ref.get_data("token").json()
    }
    requests.post(url, params=params)


def get_account(raw_value_name, Mock):
    if Mock:
        if raw_value_name == "strategy_one":
            return Account.Account.test_one
        elif raw_value_name == "strategy_two":
            return Account.Account.test_two
        elif raw_value_name == "strategy_three":
            return Account.Account.test_three
        elif raw_value_name == "strategy_four":
            return Account.Account.test_four
    else:
        if raw_value_name == "strategy_one":
            return Account.Account.one
        elif raw_value_name == "strategy_two":
            return Account.Account.two
        elif raw_value_name == "strategy_three":
            return Account.Account.three
        elif raw_value_name == "strategy_four":
            return Account.Account.four


def lambda_handler(event, context):
    print("Starting")
    if context == "not_aws":
        global is_aws
        is_aws = False
    begin()
    print("I'm sick of this shit.")
    return "Hello World"


def get_executed_price(id_to_find, symbol):
    trades = api.get_all_trades(symbol)['data']['rows']
    for trade in trades:
        if trade['orderID'] == id_to_find:
            return trade['execPriceEp'] / 10000
    return None


if __name__ == '__main__':
    lambda_handler(None, "not_aws")
