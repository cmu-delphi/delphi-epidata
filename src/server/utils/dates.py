from typing import (
    Optional,
    Sequence,
    Tuple,
    Union
)
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

def guess_time_value_is_week(value: int) -> bool:
    # YYYYWW type and not YYYYMMDD
    return len(str(value)) == 6

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

def dates_to_ranges(values: Optional[Sequence[Union[Tuple[int, int], int]]]) -> Optional[Sequence[Union[Tuple[int, int], int]]]:
    """
    Converts a mixed list of dates and date ranges to an optimized list where dates are merged into ranges where possible.
    e.g. [20200101, 20200102, (20200101, 20200104), 20200106] -> [(20200101, 20200104), 20200106]
    (the first two values of the original list are merged into a single range)
    """
    if not values or len(values) <= 1:
        return values

    # determine whether the list is of days (YYYYMMDD) or weeks (YYYYWW) based on first element
    try:
        if (isinstance(values[0], tuple) and guess_time_value_is_day(values[0][0]))\
            or (isinstance(values[0], int) and guess_time_value_is_day(values[0])):
            return days_to_ranges(values)
        elif (isinstance(values[0], tuple) and guess_time_value_is_week(values[0][0]))\
            or (isinstance(values[0], int) and guess_time_value_is_week(values[0])):
            return weeks_to_ranges(values)
        else:
            return values
    except:
        return values

def days_to_ranges(values: Sequence[Union[Tuple[int, int], int]]) -> Sequence[Union[Tuple[int, int], int]]:
    intervals = []

    # populate list of intervals based on original values
    for v in values:
        if isinstance(v, int):
            # 20200101 -> [20200101, 20200101]
            intervals.append([time_value_to_date(v), time_value_to_date(v)])
        else: # tuple
            # (20200101, 20200102) -> [20200101, 20200102]
            intervals.append([time_value_to_date(v[0]), time_value_to_date(v[1])])

    intervals.sort(key=lambda x: x[0])

    # merge overlapping intervals https://leetcode.com/problems/merge-intervals/
    merged = []
    for interval in intervals:
        # no overlap, append the interval
        # caveat: we subtract 1 from interval[0] so that contiguous intervals are considered overlapping. i.e. [1, 1], [2, 2] -> [1, 2]
        if not merged or merged[-1][1] < interval[0] - timedelta(days=1):
            merged.append(interval)
        # overlap, merge the current and previous intervals
        else:
            merged[-1][1] = max(merged[-1][1], interval[1])

    # convert intervals from dates back to integers
    ranges = []
    for m in merged:
        if m[0] == m[1]:
            ranges.append(date_to_time_value(m[0]))
        else:
            ranges.append((date_to_time_value(m[0]), date_to_time_value(m[1])))

    return ranges

def weeks_to_ranges(values: Sequence[Union[Tuple[int, int], int]]) -> Sequence[Union[Tuple[int, int], int]]:
    intervals = []

    # populate list of intervals based on original values
    for v in values:
        if isinstance(v, int):
            # 202001 -> [202001, 202001]
            intervals.append([week_value_to_week(v), week_value_to_week(v)])
        else: # tuple
            # (202001, 202002) -> [202001, 202002]
            intervals.append([week_value_to_week(v[0]), week_value_to_week(v[1])])

    intervals.sort(key=lambda x: x[0])

    # merge overlapping intervals https://leetcode.com/problems/merge-intervals/
    merged = []
    for interval in intervals:
        # no overlap, append the interval
        # caveat: we subtract 1 from interval[0] so that contiguous intervals are considered overlapping. i.e. [1, 1], [2, 2] -> [1, 2]
        if not merged or merged[-1][1] < interval[0] - 1:
            merged.append(interval)
        # overlap, merge the current and previous intervals
        else:
            merged[-1][1] = max(merged[-1][1], interval[1])

    # convert intervals from weeks back to integers
    ranges = []
    for m in merged:
        if m[0] == m[1]:
            ranges.append(week_to_time_value(m[0]))
        else:
            ranges.append((week_to_time_value(m[0]), week_to_time_value(m[1])))

    return ranges
