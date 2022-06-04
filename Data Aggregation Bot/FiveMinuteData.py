# FiveMinuteData.py
# Copyright Yush Raj Kapoor
# Created 03/21/2022

import pandas_ta as ta
import pandas as pd


class FiveMinuteData:

    def data(self, bars, is_initial=False):
        df = pd.DataFrame(data=bars)

        close = df['Close']

        ema25 = ta.ema(close, length=25)
        ema50 = ta.ema(df['Close'], length=50)
        ema100 = ta.ema(df['Close'], length=100)
        ema200 = ta.ema(df['Close'], length=200)
        std = ta.stdev(close, length=14)
        rsi = ta.rsi(close, length=28)

        engulfing = ["None"]
        for i in range(0, len(bars['Close'])-1):
            engulfing.append("None")
            if bars['Close'][i+1] > bars['Open'][i] > bars['Close'][i] >= (bars['Open'][i+1] * 0.9998):
                engulfing[i+1] = "Bullish"
            if (bars['Open'][i+1] * 1.0002) >= bars['Close'][i] > bars['Open'][i] > bars['Close'][i+1]:
                engulfing[i+1] = "Bearish"

        to_return = {
            "Time": bars["Time"],
            "Ema25": ema25.values.tolist(),
            "Ema50": ema50.values.tolist(),
            "Ema100": ema100.values.tolist(),
            "Ema200": ema200.values.tolist(),
            "RSI": rsi.values.tolist(),
            "Open": bars['Open'],
            "Close": bars['Close'],
            "Low": bars['Low'],
            "High": bars["High"],
            "Engulfing": engulfing,
            "Std": std.values.tolist(),
            "Price": bars['Close'],
            "Volume": bars['Volume']
        }

        if not is_initial:
            to_return["Price"] = bars["Price"]

        return to_return


    def directory(self):
        return ["Time", "Ema25", "Ema50", "Ema100", "Ema200", "RSI", "Open", "Close", "Low", "High", "Engulfing", "Std", "Price", "Volume"]