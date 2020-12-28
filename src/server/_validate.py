from flask import request
from typing import Iterable, List, Union, Optional, Tuple, Dict, Any
from ._printer import ValidationFailedException


def require_all(*values: Iterable[str]) -> bool:
    """
    returns true if all fields are present in the request otherwise raises an exception
    :returns bool
    """
    for value in values:
        if not request.values.get(value):
            raise ValidationFailedException(f"missing parameter: need [{values}]")
    return True


def require_any(*values: Iterable[str]) -> bool:
    """
    returns true if any fields are present in the request otherwise raises an exception
    :returns bool
    """
    for value in values:
        if request.values.get(value):
            return True
    raise ValidationFailedException(f"missing parameter: need one of [{values}]")


def extract_strings(key: str) -> Optional[List[str]]:
    s = request.values.get(key)
    if not s:
        # nothing to do
        return None
    return s.split(",")


IntRange = Union[Tuple[int, int], int]


def extract_ints(key: str) -> Optional[List[IntRange]]:
    s = request.values.get(key)
    if not s:
        # nothing to do
        return None

    def _parse_range(part: str):
        if "-" not in part:
            return int(part)
        r = part.split("-", 2)
        first = int(r[0])
        last = int(r[1])
        if first == last:
            # the first and last numbers are the same, just treat it as a singe value
            return first
        elif last > first:
            # add the range as an array
            return (first, last)
        # the range is inverted, this is an error
        return None

    values = [_parse_range(part) for part in s.split(",")]
    # check for invalid values
    return None if any(v is None for v in values) else values


def parse_date(s: str) -> int:
    # parses a given string in format YYYYMMDD or YYYY-MM-DD to a number in the form YYYYMMDD
    return int(s.replace("-", ""))


DateRange = Union[Tuple[int, int], int]


def extract_dates(s: str) -> Optional[List[DateRange]]:
    # extracts an array of values and/or ranges from a string
    #   $str: the string to parse
    if not s:
        return None
    values: List[Union[Tuple[int, int], int]] = []

    def push_range(first: str, last: str):
        first_d = parse_date(first)
        last_d = parse_date(last)
        if first_d == last_d:
            # the first and last numbers are the same, just treat it as a singe value
            return first_d
        if last_d > first_d:
            # add the range as an array
            return (first_d, last_d)
        # the range is inverted, this is an error
        return None

    parts = s.split(",")
    for part in parts:
        if "-" not in part and ":" not in part:
            # YYYYMMDD
            values.append(parse_date(part))
            continue
        if ":" in part:
            # YYYY-MM-DD:YYYY-MM-DD
            range_part = part.split(":", 2)
            r = push_range(range_part[0], range_part[1])
            if r is None:
                return None
            values.append(r)
            continue
        # YYYY-MM-DD or YYYYMMDD-YYYYMMDD
        # split on the dash
        range_part = part.split("-")
        if len(range_part) == 2:
            # YYYYMMDD-YYYYMMDD
            r = push_range(range_part[0], range_part[1])
            if r is None:
                return None
            values.append(r)
            continue
        # YYYY-MM-DD
        values.append(parse_date(part))
    # success, return the list
    return values


def filter_fields(generator: Iterable[Dict[str, Any]]):
    fields = extract_strings("fields")
    if not fields:
        yield from generator
    else:
        for row in generator:
            filtered = dict()
            for field in fields:
                if field in row:
                    filtered[field] = row[field]
            yield filtered
