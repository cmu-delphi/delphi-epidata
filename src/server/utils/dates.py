from datetime import date, timedelta
from typing import (
    Callable,
    Optional,
    Sequence,
    Tuple,
    Union
)

from epiweeks import Week, Year
from typing_extensions import TypeAlias

from delphi_utils import get_structured_logger

# Alias for a sequence of date ranges (int, int) or date integers
IntRange: TypeAlias = Union[Tuple[int, int], int]
TimeValues: TypeAlias = Sequence[IntRange]

def time_value_to_day(value: int) -> date:
    year, month, day = value // 10000, (value % 10000) // 100, value % 100
    if year < date.min.year:
        return date.min
    if year > date.max.year:
        return date.max
    return date(year=year, month=month, day=day)

def time_value_to_week(value: int) -> Week:
    year, week = value // 100, value % 100
    if year < date.min.year:
        return Week(date.min.year, 1)
    if year > date.max.year - 1:
        return Week(date.max.year - 1, 1)  # minus 1 since internally it does some checks with a year + 1
    return Week(year=year, week=week)

def guess_time_value_is_day(value: int) -> bool:
    # YYYYMMDD type and not YYYYMM
    return len(str(value)) == 8

def guess_time_value_is_week(value: int) -> bool:
    # YYYYWW type and not YYYYMMDD
    return len(str(value)) == 6

def day_to_time_value(d: date) -> int:
    return int(d.strftime("%Y%m%d"))

def week_to_time_value(w: Week) -> int:
    return w.year * 100 + w.week

def time_value_to_iso(value: int) -> str:
    return time_value_to_day(value).strftime("%Y-%m-%d")

def shift_day_value(time_value: int, days: int) -> int:
    if days == 0:
        return time_value
    d = time_value_to_day(time_value)
    shifted = d + timedelta(days=days)
    return day_to_time_value(shifted)

def shift_week_value(week_value: int, weeks: int) -> int:
    if weeks == 0:
        return week_value
    week = time_value_to_week(week_value)
    shifted = week + weeks
    return week_to_time_value(shifted)

def days_in_range(range: Tuple[int, int]) -> int:
    """
    returns the days within this time range
    """

    start = time_value_to_day(range[0])
    end = time_value_to_day(range[1])
    delta = end - start
    return delta.days + 1  # same date should lead to 1 day that will be queried

def weeks_in_range(week_range: Tuple[int, int]) -> int:
    start = time_value_to_week(week_range[0])
    end = time_value_to_week(week_range[1])
    acc = end.week - start.week
    # accumulate the number of weeks in the years between
    for y in range(start.year, end.year):
        year = Year(y)
        acc += year.totalweeks()
    return acc + 1  # same week should lead to 1 week that will be queried

def time_values_to_ranges(values: Optional[TimeValues]) -> Optional[TimeValues]:
    """
    Converts a mixed list of dates and date ranges to an optimized list where dates are merged into ranges where possible.
    e.g. [20200101, 20200102, (20200101, 20200104), 20200106] -> [(20200101, 20200104), 20200106]
    (the first two values of the original list are merged into a single range)
    """
    logger = get_structured_logger('server_utils')
    if not values or len(values) <= 1:
        logger.debug("List of dates looks like 0-1 elements, nothing to optimize", time_values=values)
        return values

    # determine whether the list is of days (YYYYMMDD) or weeks (YYYYWW) based on first element
    first_element = values[0][0] if isinstance(values[0], tuple) else values[0]
    if guess_time_value_is_day(first_element):
        logger.debug("Treating time value as day", time_value=first_element)
        return days_to_ranges(values)
    elif guess_time_value_is_week(first_element):
        logger.debug("Treating time value as week", time_value=first_element)
        return weeks_to_ranges(values)
    else:
        logger.debug("Time value unclear, not optimizing", time_value=first_element)
        return values

def days_to_ranges(values: TimeValues) -> TimeValues:
    return _to_ranges(values, time_value_to_day, day_to_time_value, timedelta(days=1))

def weeks_to_ranges(values: TimeValues) -> TimeValues:
    return _to_ranges(values, time_value_to_week, week_to_time_value, 1)

def _to_ranges(values: TimeValues, value_to_date: Callable, date_to_value: Callable, time_unit: Union[int, timedelta]) -> TimeValues:
    try:
        intervals = []

        # populate list of intervals based on original date/week values
        for v in values:
            if isinstance(v, int):
                # 20200101 -> [20200101, 20200101]
                intervals.append([value_to_date(v), value_to_date(v)])
            else: # tuple
                # (20200101, 20200102) -> [20200101, 20200102]
                intervals.append([value_to_date(v[0]), value_to_date(v[1])])

        intervals.sort()

        # merge overlapping intervals https://leetcode.com/problems/merge-intervals/
        merged = []
        for interval in intervals:
            # no overlap, append the interval
            # caveat: we subtract 1 from interval[0] so that contiguous intervals are considered overlapping. i.e. [1, 1], [2, 2] -> [1, 2]
            if not merged or merged[-1][1] < interval[0] - time_unit:
                merged.append(interval)
            # overlap, merge the current and previous intervals
            else:
                merged[-1][1] = max(merged[-1][1], interval[1])

        # convert intervals from dates/weeks back to integers
        ranges = []
        for m in merged:
            if m[0] == m[1]:
                ranges.append(date_to_value(m[0]))
            else:
                ranges.append((date_to_value(m[0]), date_to_value(m[1])))

        get_structured_logger('server_utils').debug("Optimized list of date values", original=values, optimized=ranges, original_length=len(values), optimized_length=len(ranges))

        return ranges
    except Exception as e:
        get_structured_logger('server_utils').debug('bad input to date ranges', time_values=values, exception=e)
        return values
