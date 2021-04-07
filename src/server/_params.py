import re
from dataclasses import dataclass
from typing import Any, List, Optional, Sequence, Tuple, Union

from flask import request

from ._exceptions import ValidationFailedException


def _parse_common_multi_arg(key: str) -> List[Tuple[str, Union[bool, Sequence[str]]]]:
    line = ";".join(request.values.getlist(key))

    parsed: List[Tuple[str, Union[bool, Sequence[str]]]] = []

    if not line:
        return parsed

    pattern = re.compile(r"^(\w+):(.*)$", re.MULTILINE)
    for entry in line.split(";"):
        m = pattern.match(entry)
        if not m:
            raise ValidationFailedException(f"{key} param: {entry} is not matching <{key}_type>:<{key}_values> syntax")
        group_type = m.group(1).strip()
        group_value = m.group(2).strip()
        if group_value == "*":
            parsed.append((group_type, True))
        else:
            parsed.append((group_type, [g.strip() for g in group_value.split(",")]))
    return parsed


@dataclass
class GeoPair:
    geo_type: str
    geo_values: Union[bool, Sequence[str]]


def parse_geo_arg() -> List[GeoPair]:
    return [GeoPair(geo_type, geo_values) for [geo_type, geo_values] in _parse_common_multi_arg("geo")]


@dataclass
class SourceSignalPair:
    source: str
    signal: Union[bool, Sequence[str]]


def parse_source_signal_arg() -> List[SourceSignalPair]:
    return [SourceSignalPair(source, signals) for [source, signals] in _parse_common_multi_arg("signal")]


@dataclass
class TimePair:
    time_type: str
    time_values: Union[bool, Sequence[Union[int, Tuple[int, int]]]]


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
    msg = f"{time_value} is not matching a known format YYYYMMDD, YYYY-MM-DD, YYYYMMDD-YYYYMMDD, or YYYY-MM-DD--YYYY-MM-DD"

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


def parse_time_arg() -> List[TimePair]:
    def parse(time_type: str, time_values: Union[bool, Sequence[str]]) -> TimePair:
        if isinstance(time_values, bool):
            return TimePair(time_type, time_values)

        if time_type == "week":
            return TimePair("week", [parse_week_value(t) for t in time_values])
        elif time_type == "day":
            return TimePair("day", [parse_day_value(t) for t in time_values])
        raise ValidationFailedException(f'time param: {time_type} is not one of "day" or "week"')

    return [parse(time_type, time_values) for [time_type, time_values] in _parse_common_multi_arg("time")]
