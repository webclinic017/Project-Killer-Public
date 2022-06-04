# OneHourData.py
# Copyright Yush Raj Kapoor
# Created 03/21/2022

import pandas_ta as ta
import pandas as pd


class OneHourData:

    def data(self, bars, is_initial=False):
        compressed_bars = {}
        for i in bars:
            bar_in_question = bars[i]
            compressed_bars[i] = bar_in_question[-int(len(bar_in_question) / 11):]
        df = pd.DataFrame(data=compressed_bars)
        ema_df = pd.DataFrame(data=bars)
        if is_initial:
            df = ema_df

        close = df['Close']

        ema200 = None
        if is_initial:
            ema200_array = ta.ema(ema_df['Close'], length=200).values
            ema200 = pd.Series(ema200_array)
        else:
            ema200_array = ta.ema(ema_df['Close'], length=200).iloc[-len(close):].values
            ema200 = pd.Series(ema200_array)

        rsi = ta.rsi(close, length=14)

        stochastic = ta.stoch(df['High'], df['Low'], close, smooth_k=2)
        k_data = stochastic["STOCHk_14_3_2"]
        d_data = stochastic["STOCHd_14_3_2"]

        wb_tsv = ta.wb_tsv(close, df['Volume'], length=13, signal=7)
        tsv = wb_tsv["TSV_13_7"]
        supertrend10_data = ta.supertrend(df['High'], df['Low'], close, 10, 1)
        supertrend11_data = ta.supertrend(df['High'], df['Low'], close, 11, 2)
        supertrend12_data = ta.supertrend(df['High'], df['Low'], close, 12, 3)
        supertrend10_direction = supertrend10_data["SUPERTd_10_1"]
        supertrend11_direction = supertrend11_data["SUPERTd_11_2"]
        supertrend12_direction = supertrend12_data["SUPERTd_12_3"]
        supertrend10_value = supertrend10_data["SUPERT_10_1"]
        supertrend11_value = supertrend11_data["SUPERT_11_2"]
        supertrend12_value = supertrend12_data["SUPERT_12_3"]

        bollinger = ta.bbands(ema_df['Close'], 20, 2)
        bollinger_lower = bollinger["BBL_20_2"]
        bollinger_middle = bollinger["BBM_20_2"]
        bollinger_upper = bollinger["BBU_20_2"]
        bollinger_distance = bollinger_upper - bollinger_lower
        lowest_of = 60
        relevant_distance = bollinger_distance.iloc[-lowest_of:]
        bollinger_validation = [False] * len(bollinger)
        if relevant_distance.iloc[-1] <= relevant_distance.min():
            bollinger_validation[-1] = True

        to_return = {
            "Time": bars['Time'],
            "Ema200": ema200.values.tolist(),
            "RSI": rsi.values.tolist(),
            "K_Data": k_data.values.tolist(),
            "D_Data": d_data.values.tolist(),
            "Open": bars['Open'],
            "Close": bars['Close'],
            "High": bars['High'],
            "Low": bars['Low'],
            "Volume": bars['Volume'],
            "TSV": tsv.values.tolist(),
            "Supertrend_Direction10": supertrend10_direction.values.tolist(),
            "Supertrend_Direction11": supertrend11_direction.values.tolist(),
            "Supertrend_Direction12": supertrend12_direction.values.tolist(),
            "Supertrend_Value10": supertrend10_value.values.tolist(),
            "Supertrend_Value11": supertrend11_value.values.tolist(),
            "Supertrend_Value12": supertrend12_value.values.tolist(),
            "Price": bars['Close'],
            "Bollinger_Low": bollinger_lower.values.tolist(),
            "Bollinger_Middle": bollinger_middle.values.tolist(),
            "Bollinger_High": bollinger_upper.values.tolist(),
            "Bollinger_Validation": bollinger_validation,
        }

        if not is_initial:
            to_return["Price"] = bars["Price"]

        return to_return

    def directory(self):
        return ["Time", "Ema200", "RSI", "K_Data", "D_Data", "Open", "Close", "High", "Low", "Volume", "TSV", "Supertrend_Direction10", "Supertrend_Direction11", "Supertrend_Direction12", "Supertrend_Value10", "Supertrend_Value11", "Supertrend_Value12", "Price", "Bollinger_Low", "Bollinger_Middle", "Bollinger_High", "Bollinger_Validation"]
