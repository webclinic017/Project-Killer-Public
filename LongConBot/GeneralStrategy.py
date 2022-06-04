
from Account import Account


def get_buy_price():
    account = Account.real
    alpaca = account.alpaca_account()
    return alpaca.get_latest_crypto_quote("BTCUSD", "ERSX").__getattr__("ap")


def get_sell_price():
    account = Account.real
    alpaca = account.alpaca_account()
    return alpaca.get_latest_crypto_quote("BTCUSD", "ERSX").__getattr__("bp")


def get_coins_and_usd(account):
    alpaca = account.alpaca_account()
    coins = 0.0
    account = alpaca.get_account()
    available_usd = account.__getattr__('cash')
    if alpaca.list_positions():
        position = alpaca.get_position("BTCUSD")
        coins = position.__getattr__('qty')

    return coins, available_usd
