# lambda_function.py

import json
import firebase as ref


def collect_trash():
    rolling_aggregate_data = ref.get_data("rolling_aggregate_data").json()
    active_currencies = ref.get_data("active_currencies").json()
    for interval in rolling_aggregate_data:
        interval_data = rolling_aggregate_data[interval]
        currencies = interval_data.keys()
        for currency in currencies:
            if currency not in active_currencies:
                print("Deleting: " + currency)
                ref.delete_data("rolling_aggregate_data/" + interval + "/" + currency)

    print("Trash Collection Complete!")


def lambda_handler(event, context):
    print("Starting Trash Collector")
    collect_trash()


if __name__ == '__main__':
    lambda_handler(None, None)

