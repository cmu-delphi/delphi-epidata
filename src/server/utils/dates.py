from typing import List, Tuple
from datetime import date, timedelta
from epiweeks import Week, Year


def time_value_to_date(value: int) -> date:
    year, month, day = value // 10000, (value % 10000) // 100, value % 100
    if year < date.min.year:
        return date.min
    if year > date.max.year:
        return date.max
    return date(year=year, month=month, day=day)

def week_value_to_week(value: int) -> Week:
    year, week = value // 100, value % 100
    if year < date.min.year:
        return Week(date.min.year, 1)
    if year > date.max.year - 1:
        return Week(date.max.year - 1, 1)  # minus 1 since internally it does some checks with a year + 1
    return Week(year=year, week=week)

def guess_time_value_is_day(value: int) -> bool:
    # YYYYMMDD type and not YYYYMM
    return len(str(value)) > 6

def date_to_time_value(d: date) -> int:
    return int(d.strftime("%Y%m%d"))


def week_to_time_value(w: Week) -> int:
    return w.year * 100 + w.week

def time_value_to_iso(value: int) -> str:
    return time_value_to_date(value).strftime("%Y-%m-%d")


def shift_time_value(time_value: int, days: int) -> int:
    if days == 0:
        return time_value
    d = time_value_to_date(time_value)
    shifted = d + timedelta(days=days)
    return date_to_time_value(shifted)

def shift_week_value(week_value: int, weeks: int) -> int:
    if weeks == 0:
        return week_value
    week = week_value_to_week(week_value)
    shifted = week + weeks
    return week_to_time_value(shifted)

def days_in_range(range: Tuple[int, int]) -> int:
    """
    returns the days within this time range
    """

    start = time_value_to_date(range[0])
    end = time_value_to_date(range[1])
    delta = end - start
    return delta.days + 1  # same date should lead to 1 day that will be queried

def weeks_in_range(week_range: Tuple[int, int]) -> int:
    start = week_value_to_week(week_range[0])
    end = week_value_to_week(week_range[1])
    acc = end.week - start.week
    # accumulate the number of weeks in the years between
    for y in range(start.year, end.year):
        year = Year(y)
        acc += year.totalweeks()
    return acc + 1  # same week should lead to 1 week that will be queried

def time_value_range(range: Tuple[int, int]) -> List[int]:
    """Return a list of ints corresponding to a time range."""
    start, end = range
    if start >= end:
        return [start]
    current_date = time_value_to_date(start)
    time_values = [start]
    while time_values[-1] != end:
        current_date = current_date + timedelta(days=1)
        time_values.append(date_to_time_value(current_date))
    return time_values
