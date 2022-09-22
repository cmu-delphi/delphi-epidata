from typing import (
    Optional,
    Sequence,
    Tuple,
    Union
)
from datetime import date, timedelta
from operator import itemgetter
from itertools import groupby
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

def dates_to_ranges(values: Optional[Sequence[Union[Tuple[int, int], int]]]) -> Optional[Sequence[Union[Tuple[int, int], int]]]:
    """
    Converts a mixed list of dates and date ranges to an optimized list where dates are merged into ranges where possible.
    e.g. [20200101, 20200102, (20200101, 20200104), 20200106] -> [(20200101, 20200104), 20200106]
    (the first two values of the original list are merged into a single range)
    """
    if not values or len(values) == 0:
        return values

    # determine whether the list is of days (YYYYMMDD) or weeks (YYYYWW) based on first element
    if (isinstance(values[0], tuple) and guess_time_value_is_day(values[0][0]))\
        or (isinstance(values[0], int) and guess_time_value_is_day(values[0])):
        return days_to_ranges(values)
    else:
        return weeks_to_ranges(values)

def days_to_ranges(values: Sequence[Union[Tuple[int, int], int]]) -> Sequence[Union[Tuple[int, int], int]]:
    dates = []

    # populate list of days
    for v in values:
        if isinstance(v, int):
            dates.append(time_value_to_date(v))
        else: # tuple
            start_date = time_value_to_date(v[0])
            end_date = time_value_to_date(v[1])
            # add all dates between start and end, inclusive of end date
            dates.extend([start_date + timedelta(n) for n in range(int((end_date - start_date).days) + 1)])

    # remove duplicates then sort
    dates = sorted(list(set(dates)))

    # group consecutive values together https://docs.python.org/2.6/library/itertools.html#examples then iterate through the groups
    ranges = []
    keyfunc = lambda t: t[1] - timedelta(days=t[0])
    for _, group in groupby(enumerate(dates), keyfunc):
        group = list(group)
        if len(group) == 1:
            # group with a single date: just add that date
            ranges.append(date_to_time_value(group[0][1]))
        else:
            # group with multiple date: add first and last dates as a tuple, omit other dates as they are included within the range
            ranges.append((date_to_time_value(group[0][1]), date_to_time_value(group[-1][1])))
    return ranges

def weeks_to_ranges(values: Sequence[Union[Tuple[int, int], int]]) -> Sequence[Union[Tuple[int, int], int]]:
    weeks = []

    # populate list of weeks
    for v in values:
        if isinstance(v, int):
            weeks.append(week_value_to_week(v))
        else: # tuple
            start_week = week_value_to_week(v[0])
            end_week = week_value_to_week(v[1])
            # add all weeks between start and end, inclusive of end week
            while start_week <= end_week:
                weeks.append(start_week)
                start_week += 1
    
    # remove duplicates then sort
    weeks = sorted(list(set(weeks)))

    # group consecutive values together https://docs.python.org/2.6/library/itertools.html#examples then iterate through the groups
    ranges = []
    keyfunc = lambda t: t[1] - t[0]
    for _, group in groupby(enumerate(weeks), keyfunc):
        group = list(group)
        if len(group) == 1:
            # group with a single date: just add that date
            ranges.append(week_to_time_value(group[0][1]))
        else:
            # group with multiple date: add first and last dates as a tuple, omit other dates as they are included within the range
            ranges.append((week_to_time_value(group[0][1]), week_to_time_value(group[-1][1])))
    return ranges
