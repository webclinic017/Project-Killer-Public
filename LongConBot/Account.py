import enum
import credentials
import alpaca_trade_api


class Account(enum.Enum):
    real = 0
    paper1 = 1

    def key(self):
        creds = credentials.decoded_credentials
        if self == Account.real:
            return creds["ALPACA_API_KEY"]
        elif self == Account.paper1:
            return creds["PAPER_1_KEY"]

    def secret(self):
        creds = credentials.decoded_credentials
        if self == Account.real:
            return creds["ALPACA_API_SECRET"]
        elif self == Account.paper1:
            return creds["PAPER_1_SECRET"]

    def url(self):
        if self == Account.real:
            return "https://api.alpaca.markets"
        elif self == Account.paper1:
            return "https://paper-api.alpaca.markets"

    def strategy(self):
        if self == Account.real:
            return None
        elif self == Account.paper1:
            return "strategy_one"

    def alpaca_account(self):
        return alpaca_trade_api.REST(self.key(), self.secret(), self.url(), 'v2')

