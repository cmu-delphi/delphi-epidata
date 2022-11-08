from typing import List, Optional, Sequence, Tuple, Union

from flask import request

from ._exceptions import ValidationFailedException


def require_all(*values: str) -> bool:
    """
    returns true if all fields are present in the request otherwise raises an exception
    :returns bool
    """
    for value in values:
        if not request.values.get(value):
            raise ValidationFailedException(f"missing parameter: need [{', '.join(values)}]")
    return True


def require_any(*values: str, empty=False) -> bool:
    """
    returns true if any fields are present in the request otherwise raises an exception
    :returns bool
    """
    for value in values:
        if request.values.get(value) or (empty and value in request.values):
            return True
    raise ValidationFailedException(f"missing parameter: need one of [{', '.join(values)}]")


def _extract_value(key: Union[str, Sequence[str]]) -> Optional[str]:
    if isinstance(key, str):
        return request.values.get(key)
    for k in key:
        if k in request.values:
            return request.values[k]
    return None


def _extract_list_value(key: Union[str, Sequence[str]]) -> List[str]:
    if isinstance(key, str):
        return request.values.getlist(key)
    for k in key:
        if k in request.values:
            return request.values.getlist(k)
    return []


def extract_strings(key: Union[str, Sequence[str]]) -> Optional[List[str]]:
    s = _extract_list_value(key)
    if not s:
        # nothing to do
        return None
    # we can have multiple values
    return [v for vs in s for v in vs.split(",")]


IntRange = Union[Tuple[int, int], int]


def extract_integer(key: Union[str, Sequence[str]]) -> Optional[int]:
    s = _extract_value(key)
    if not s:
        # nothing to do
        return None
    try:
        return int(s)
    except ValueError:
        raise ValidationFailedException(f"{key}: not a number: {s}")


def extract_integers(key: Union[str, Sequence[str]]) -> Optional[List[IntRange]]:
    parts = extract_strings(key)
    if not parts:
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
        raise ValidationFailedException(f"{key}: the given range is inverted")

    try:
        values = [_parse_range(part) for part in parts]
        # check for invalid values
        return None if any(v is None for v in values) else values
    except ValueError as e:
        raise ValidationFailedException(f"{key}: not a number: {str(e)}")


def parse_date(s: str) -> int:
    # parses a given string in format YYYYMMDD or YYYY-MM-DD to a number in the form YYYYMMDD
    try:
        return int(s.replace("-", ""))
    except ValueError:
        raise ValidationFailedException(f"not a valid date: {s}")


def extract_date(key: Union[str, Sequence[str]]) -> Optional[int]:
    s = _extract_value(key)
    if not s:
        return None
    return parse_date(s)


DateRange = Union[Tuple[int, int], int]


def extract_dates(key: Union[str, Sequence[str]]) -> Optional[List[DateRange]]:
    parts = extract_strings(key)
    if not parts:
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
        raise ValidationFailedException(f"{key}: the given range is inverted")

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
