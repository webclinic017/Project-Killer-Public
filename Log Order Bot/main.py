# main.py
# Created 03/24/2022
# Copyright Yush Raj Kapoor

import firebase as ref
import phemex
import Account
import json

Mock = ref.get_data("Mock").json()
api: phemex.Client = phemex.Client()


def begin(currency, strategy):
    order_data = ref.get_data(currency + "/orders/" + strategy).json()

    all_ids = []
    all_orders = {}
    if order_data is not None:
        for order_id in order_data:
            order = order_data[order_id]
            if order['ordStatus'] != api.OrderStatus.untriggered.value:
                all_ids.append(order["orderID"])
                order['strategy'] = strategy
                all_orders[order["orderID"]] = order
    print("Database Query for " + currency + " complete")

    check_all_ids = []
    check_all_orders = {}
    account = get_account(strategy)
    api.update_client(account, Mock)
    all_orders_phemex = api.get_all_orders(currency + "USD")['data']['rows']
    for order in all_orders_phemex:
        check_all_ids.append(order['orderID'])
        check_all_orders[order["orderID"]] = order
    print("Phemex Query for " + currency + " complete")

    # Cross checks data between firebase and Phemex to see if there are any new orders
    orders_to_add = []
    for order_id in check_all_ids:
        if order_id not in all_ids:
            orders_to_add.append(check_all_orders[order_id])

    # These new orders are then added to firebase using their orderID as the key
    for order in orders_to_add:
        order['strategy'] = strategy
        all_orders[order['orderID']] = order
        print("Added Order for " + currency)
        ref.update_firebase(currency + "/orders/" + strategy + "/" + str(order['orderID']), order)

    # finds all open orders using Phemex data and adds them to firebase,
    # regardless of whether they were there before or not
    untriggered_ids = []
    for order_id in check_all_ids:
        order = check_all_orders[order_id]
        status = order['ordStatus']
        if status == "Untriggered":
            untriggered_ids.append(order['orderID'])
    ref.update_firebase(currency + "/open_orders/" + strategy, untriggered_ids)


def get_account(raw_value_name):
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
    base_obj = None
    if "queryStringParameters" in event:
        base_obj = event["queryStringParameters"]
    else:
        base_obj = json.loads(event['Records'][0]['body'])
    currency = base_obj["currency"]
    strategy = base_obj["strategy"]
    begin(currency, strategy)
    print("Again? Motherfucker, Again?")
    return "Hello World"


if __name__ == '__main__':
    evt = {
        "queryStringParameters": {
            "currency": "BTC",
            "strategy": "strategy_three"
        }
    }
    lambda_handler(evt, None)
