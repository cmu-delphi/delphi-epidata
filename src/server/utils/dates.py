from typing import Tuple
from datetime import date, timedelta


def time_value_to_date(value: int) -> date:
    year, month, day = value // 10000, (value % 10000) // 100, value % 100
    return date(year=year, month=month, day=day)


def date_to_time_value(d: date) -> int:
    return int(d.strftime("%Y%m%d"))


def time_value_to_iso(value: int) -> str:
    return time_value_to_date(value).strftime("%Y-%m-%d")


def shift_time_value(time_value: int, days: int) -> int:
    if days == 0:
        return time_value
    d = time_value_to_date(time_value)
    shifted = d + timedelta(days=days)
    return date_to_time_value(shifted)


def days_in_range(range: Tuple[int, int]) -> int:
    """
    returns the days within this time range
    """
    start = time_value_to_date(range[0])
    end = time_value_to_date(range[1])
    delta = end - start
    return delta.days + 1  # same date should lead to 1 day that will be queried