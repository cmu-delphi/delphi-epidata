from math import inf
import re
from dataclasses import dataclass
from typing import List, Optional, Sequence, Tuple, Union

from flask import request


from ._exceptions import ValidationFailedException
from .utils import days_in_range, weeks_in_range, guess_time_value_is_day


def _parse_common_multi_arg(key: str) -> List[Tuple[str, Union[bool, Sequence[str]]]]:
    # support multiple request parameter with the same name
    line = ";".join(request.values.getlist(key))

    parsed: List[Tuple[str, Union[bool, Sequence[str]]]] = []

    if not line:
        return parsed

    pattern: re.Pattern[str] = re.compile(r"^([\w\-_]+):(.*)$", re.MULTILINE)
    for entry in line.split(";"):
        m: Optional[re.Match[str]] = pattern.match(entry)
        if not m:
            raise ValidationFailedException(f"{key} param: {entry} is not matching <{key}_type>:<{key}_values> syntax")
        group_type: str = m.group(1).strip().lower()
        group_value: str = m.group(2).strip().lower()
        if group_value == "*":
            parsed.append((group_type, True))
        else:
            parsed.append((group_type, [g.strip() for g in group_value.split(",")]))
    return parsed


def _parse_single_arg(key: str) -> Tuple[str, str]:
    """
    parses a single pair
    """
    v = request.values.get(key)
    if not v:
        raise ValidationFailedException(f"{key} param is required")
    pattern: re.Pattern[str] = re.compile(r"^([\w\-_]+):([\w\-_]+)$", re.MULTILINE)
    m: Optional[re.Match[str]] = pattern.match(v)
    if not v or not m:
        raise ValidationFailedException(f"{key} param: is not matching <{key}_type>:<{key}_value> syntax")
    return m.group(1).strip().lower(), m.group(2).strip().lower()


@dataclass
class GeoPair:
    geo_type: str
    geo_values: Union[bool, Sequence[str]]

    def matches(self, geo_type: str, geo_value: str) -> bool:
        return self.geo_type == geo_type and (self.geo_values == True or (not isinstance(self.geo_values, bool) and geo_value in self.geo_values))

    def count(self) -> float:
        """
        returns the count of items in this pair
        """
        if isinstance(self.geo_values, bool):
            return inf if self.geo_values else 0
        return len(self.geo_values)


def parse_geo_arg(key: str = "geo") -> List[GeoPair]:
    return [GeoPair(geo_type, geo_values) for [geo_type, geo_values] in _parse_common_multi_arg(key)]


def parse_single_geo_arg(key: str) -> GeoPair:
    """
    parses a single geo pair with only one value
    """
    r = _parse_single_arg(key)
    return GeoPair(r[0], [r[1]])


@dataclass
class SourceSignalPair:
    source: str
    signal: Union[bool, Sequence[str]]

    def matches(self, source: str, signal: str) -> bool:
        return self.source == source and (self.signal == True or (not isinstance(self.signal, bool) and signal in self.signal))

    def count(self) -> float:
        """
        returns the count of items in this pair
        """
        if isinstance(self.signal, bool):
            return inf if self.signal else 0
        return len(self.signal)


def parse_source_signal_arg(key: str = "signal") -> List[SourceSignalPair]:
    return [SourceSignalPair(source, signals) for [source, signals] in _parse_common_multi_arg(key)]


def parse_single_source_signal_arg(key: str) -> SourceSignalPair:
    """
    parses a single source signal pair with only one value
    """
    r = _parse_single_arg(key)
    return SourceSignalPair(r[0], [r[1]])


@dataclass
class TimePair:
    time_type: str
    time_values: Union[bool, Sequence[Union[int, Tuple[int, int]]]]

    @property
    def is_week(self) -> bool:
        return self.time_type == 'week'

    @property
    def is_day(self) -> bool:
        return self.time_type != 'week'


    def count(self) -> float:
        """
        returns the count of items in this pair
        """
        if isinstance(self.time_values, bool):
            return inf if self.time_values else 0
        if self.time_type == 'week':
            return sum(1 if isinstance(v, int) else weeks_in_range(v) for v in self.time_values)
        return sum(1 if isinstance(v, int) else days_in_range(v) for v in self.time_values)


def _verify_range(start: int, end: int) -> Union[int, Tuple[int, int]]:
    if start == end:
        # the first and last numbers are the same, just treat it as a singe value
        return start
    elif end > start:
        # add the range as an array
        return (start, end)
    # the range is inverted, this is an error
    raise ValidationFailedException(f"the given range {start}-{end} is inverted")


def parse_week_value(time_value: str) -> Union[int, Tuple[int, int]]:
    count_dashes = time_value.count("-")
    msg = f"{time_value} does not match a known format YYYYWW or YYYYWW-YYYYWW"

    if count_dashes == 0:
        # plain delphi date YYYYWW
        if not re.match(r"^(\d{6})$", time_value, re.MULTILINE):
            raise ValidationFailedException(msg)
        return int(time_value)

    if count_dashes == 1:
        # delphi date range YYYYWW-YYYYWW
        if not re.match(r"^(\d{6})-(\d{6})$", time_value, re.MULTILINE):
            raise ValidationFailedException(msg)
        [first, last] = time_value.split("-", 2)
        return _verify_range(int(first), int(last))

    raise ValidationFailedException(msg)


def parse_day_value(time_value: str) -> Union[int, Tuple[int, int]]:
    count_dashes = time_value.count("-")
    msg = f"{time_value} does not match a known format YYYYMMDD, YYYY-MM-DD, YYYYMMDD-YYYYMMDD, or YYYY-MM-DD--YYYY-MM-DD"

    if count_dashes == 0:
        # plain delphi date YYYYMMDD
        if not re.match(r"^(\d{8})$", time_value, re.MULTILINE):
            raise ValidationFailedException(msg)
        return int(time_value)

    if count_dashes == 2:
        # iso date YYYY-MM-DD
        if not re.match(r"^(\d{4}-\d{2}-\d{2})$", time_value, re.MULTILINE):
            raise ValidationFailedException(msg)
        return int(time_value.replace("-", ""))

    if count_dashes == 1:
        # delphi date range YYYYMMDD-YYYYMMDD
        if not re.match(r"^(\d{8})-(\d{8})$", time_value, re.MULTILINE):
            raise ValidationFailedException(msg)
        [first, last] = time_value.split("-", 2)
        return _verify_range(int(first), int(last))

    if count_dashes == 6:
        # delphi iso date range YYYY-MM-DD--YYYY-MM-DD
        if not re.match(r"^(\d{4}-\d{2}-\d{2})--(\d{4}-\d{2}-\d{2})$", time_value, re.MULTILINE):
            raise ValidationFailedException(msg)
        [first, last] = time_value.split("--", 2)
        return _verify_range(int(first.replace("-", "")), int(last.replace("-", "")))

    raise ValidationFailedException(msg)


def _parse_time_pair(time_type: str, time_values: Union[bool, Sequence[str]]) -> TimePair:
    if isinstance(time_values, bool):
        return TimePair(time_type, time_values)

    if time_type == "week":
        return TimePair("week", [parse_week_value(t) for t in time_values])
    elif time_type == "day":
        return TimePair("day", [parse_day_value(t) for t in time_values])
    raise ValidationFailedException(f'time param: {time_type} is not one of "day" or "week"')


def parse_time_arg(key: str = "time") -> List[TimePair]:
    return [_parse_time_pair(time_type, time_values) for [time_type, time_values] in _parse_common_multi_arg(key)]


def parse_single_time_arg(key: str) -> TimePair:
    """
    parses a single time pair with only one value
    """
    r = _parse_single_arg(key)
    return _parse_time_pair(r[0], [r[1]])


def parse_day_range_arg(key: str) -> Tuple[int, int]:
    v = request.values.get(key)
    if not v:
        raise ValidationFailedException(f"{key} param is required")
    r = parse_day_value(v)
    if not isinstance(r, tuple):
        raise ValidationFailedException(f"{key} must match YYYYMMDD-YYYYMMDD or YYYY-MM-DD--YYYY-MM-DD")
    return r


def parse_day_arg(key: str) -> int:
    v = request.values.get(key)
    if not v:
        raise ValidationFailedException(f"{key} param is required")
    r = parse_day_value(v)
    if not isinstance(r, int):
        raise ValidationFailedException(f"{key} must match YYYYMMDD or YYYY-MM-DD")
    return r

def parse_week_arg(key: str) -> int:
    v = request.values.get(key)
    if not v:
        raise ValidationFailedException(f"{key} param is required")
    r = parse_week_value(v)
    if not isinstance(r, int):
        raise ValidationFailedException(f"{key} must match YYYYWW")
    return r


def parse_week_range_arg(key: str) -> Tuple[int, int]:
    v = request.values.get(key)
    if not v:
        raise ValidationFailedException(f"{key} param is required")
    r = parse_week_value(v)
    if not isinstance(r, tuple):
        raise ValidationFailedException(f"{key} must match YYYYWW-YYYYWW")
    return r

def parse_day_or_week_arg(key: str, default_value: Optional[int] = None) -> Tuple[int, bool]:
    v = request.values.get(key)
    if not v:
        if default_value is not None:
            return default_value, guess_time_value_is_day(default_value)
        raise ValidationFailedException(f"{key} param is required")
    # format is either YYYY-MM-DD or YYYYMMDD or YYYYMM
    is_week = len(v) == 6
    if is_week:
        return parse_week_arg(key), False
    return parse_day_arg(key), True

def parse_day_or_week_range_arg(key: str) -> Tuple[Tuple[int, int], bool]:
    v = request.values.get(key)
    if not v:
        raise ValidationFailedException(f"{key} param is required")
    # format is either YYYY-MM-DD--YYYY-MM-DD or YYYYMMDD-YYYYMMDD or YYYYMM-YYYYMM
    # so if the first before the - has length 6, it must be a week
    is_week = len(v.split('-', 2)[0]) == 6
    if is_week:
        return parse_week_range_arg(key), False
    return parse_day_range_arg(key), True
