# FifteenMinuteData.py
# Copyright Yush Raj Kapoor
# Created 03/21/2022

import pandas_ta as ta
import pandas as pd


class FifteenMinuteData:

    def data(self, bars, is_initial=False):
        df = pd.DataFrame(data=bars)

        close = df['Close']

        rsi = ta.rsi(close, length=14)

        macd_signal = ta.macd(close, 26, 12)
        macd = macd_signal["MACD_12_26_9"]
        signal = macd_signal["MACDs_12_26_9"]

        stochastic = ta.stoch(df["High"], df['Low'], close, smooth_k=2)
        k_data = stochastic["STOCHk_14_3_2"]
        d_data = stochastic["STOCHd_14_3_2"]

        to_return = {
                "Time": bars['Time'],
                "RSI": rsi.values.tolist(),
                "Macd": macd.values.tolist(),
                "Signal": signal.values.tolist(),
                "K_Data": k_data.values.tolist(),
                "D_Data": d_data.values.tolist(),
                "Open": bars['Open'],
                "Close": bars['Close'],
                "Low": bars['Low'],
                "High": bars["High"],
                "Price": bars['Close'],
                "Volume": bars['Volume']
            }

        if not is_initial:
            to_return["Price"] = bars["Price"]

        return to_return


    def directory(self):
        return ["Time", "RSI", "Macd", "Signal", "K_Data", "D_Data", "Open", "Close", "Low", "High", "Price", "Volume"]

