# IntervalData.py
# Copyright Yush Raj Kapoor
# Created 05/11/2022

import enum
import FiveMinuteData
import FifteenMinuteData
import OneHourData


def default_directory():
    return ["Time", "Open", "Close", "Low", "High", "Volume", "Price"]


class IntervalData(enum.Enum):
    five_minute_data = 5
    fifteen_minute_data = 15
    one_hour_data = 60

    def get_data(self):
        if self == IntervalData.five_minute_data:
            return FiveMinuteData.FiveMinuteData()
        elif self == IntervalData.fifteen_minute_data:
            return FifteenMinuteData.FifteenMinuteData()
        elif self == IntervalData.one_hour_data:
            return OneHourData.OneHourData()

    def deletion_limit(self):
        return int(self.period_days() * 24 * (60 / self.value)) + 1

    def merge_data(self, old_data, new_data):
        data_to_return = {}
        directory = default_directory()
        delta = self.value * 60
        new_tm = new_data["Time"]

        while old_data["Time"][-1] + delta > new_tm:
            for i in old_data:
                old_data[i].pop(-1)

        for i in directory:
            data_to_return[i] = old_data[i]
            val = 0
            if i in new_data:
                val = new_data[i]
            old_data[i].append(val)

        return data_to_return

    def delete_first(self, data):
        directory = self.get_data().directory()
        for i in directory:
            data[i].pop(0)
        return data

    def blank_data(self):
        data = {}
        directory = self.get_data().directory()
        for i in directory:
            data[i] = [0] * self.deletion_limit()
        return data

    def add_ta(self, bars, is_initial=False):
        all_entries = self.get_data().data(bars, is_initial)
        return all_entries

    def period_days(self):
        if self == IntervalData.five_minute_data:
            return 0.8
        if self == IntervalData.fifteen_minute_data:
            return 0.5
        if self == IntervalData.one_hour_data:
            return 8.5

    def is_correct_format(self, data):
        directory = default_directory()
        for i in directory:
            if i not in data:
                return False
        return True


def get_interval_data(value):
    if value == 5:
        return IntervalData.five_minute_data
    elif value == 15:
        return IntervalData.fifteen_minute_data
    elif value == 60:
        return IntervalData.one_hour_data



