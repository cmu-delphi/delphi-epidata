from flask import request
from typing import Iterable, List, Union, Optional
from ._printer import APrinter


def require_all(printer: APrinter, *values: Iterable[str]) -> bool:
    """
    returns true if all fields are present in the request
    :returns bool
    """
    for value in values:
        if not request.values.get(value):
            printer.print_validation_failed(f"missing parameter: need [{values}]")
            return False
    return True


def require_any(printer: APrinter, *values: Iterable[str]) -> bool:
    """
    returns true if any fields are present in the request
    :returns bool
    """
    for value in values:
        if request.values.get(value):
            return True
    printer.print_validation_failed(f"missing parameter: need one of [{values}]")
    return False


def date_string(value: int) -> str:
    # converts a date integer (YYYYMMDD) into a date string (YYYY-MM-DD)
    # $value: the date as an 8-digit integer
    year = int(value / 10000) % 10000
    month = int(value / 100) % 100
    day = value % 100
    return "{0:04d}-{1:02d}-{2:%02d}".format(year, month, day)


def extract_values(
    s: str, value_type="str"
) -> Optional[List[Union[Tuple[str, str], Tuple[int, int], str, int]]]:
    # extracts an array of values and/or ranges from a string
    #   $str: the string to parse
    #   $type:
    #     - 'int': interpret dashes as ranges, cast values to integers
    #     - 'ordered_string': interpret dashes as ranges, keep values as strings
    #     - otherwise: ignore dashes, keep values as strings
    if not str:
        # nothing to do
        return None
    # whether to parse a value with a dash as a range of values
    should_parse_range = value_type == "int" or value_type == "ordered_string"
    # maintain a list of values and/or ranges
    values: List[Union[Tuple[str, str], Tuple[int, int], str, int]] = []
    # split on commas and loop over each entry, which could be either a single value or a range of values
    parts = s.split(",")
    for part in parts:
        if should_parse_range and "-" in part:
            # split on the dash
            [first, last] = part.split("-", 2)
            if value_type == "int":
                first = int(first)
                last = int(last)
            if first == last:
                # the first and last numbers are the same, just treat it as a singe value
                values.append(first)
            elif last > first:
                # add the range as an array
                values.append((first, last))
            else:
                # the range is inverted, this is an error
                return None
        else:
            # this is a single value
            if value_type == "int":
                # cast to integer
                value = int(part)
            else:
                # interpret the string literally
                value = part
            # add the extracted value to the list
            values.append(value)
    # success, return the list
    return values


def parse_date(s: str) -> int:
    # parses a given string in format YYYYMMDD or YYYY-MM-DD to a number in the form YYYYMMDD
    return int(s.replace("-", ""))


def extract_dates(s: str) -> Optional[List[Union[Tuple[int, int], int]]]:
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