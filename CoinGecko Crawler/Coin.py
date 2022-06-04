# Coin.py
# Created 05/15/22
# Copyright Yush Raj Kapoor


class Coin:

    def __init__(self, info):
        self.geckoID = info["id"]
        self.ticker = info["symbol"]
        self.displayName = info["name"]
        if "market_cap_rank" in info:
            self.marketCap = info["market_cap_rank"]
        if "image" in info:
            self.geckoImageURL = info["image"]



