from ._db import metadata
from typing import Optional, Sequence, Union, Tuple, Dict, Any
from ._validate import DateRange
from ._printer import create_printer
from ._common import db
from sqlalchemy import text
from ._validate import extract_strings


def date_string(value: int) -> str:
    # converts a date integer (YYYYMMDD) into a date string (YYYY-MM-DD)
    # $value: the date as an 8-digit integer
    year = int(value / 10000) % 10000
    month = int(value / 100) % 100
    day = value % 100
    return "{0:04d}-{1:02d}-{2:02d}".format(year, month, day)


def to_condition(
    field: str,
    value: Union[Tuple[str, str], str, Tuple[int, int], int],
    param_key: str,
    params: Dict[str, Any],
    formatter=lambda x: x,
):
    if isinstance(value, (list, tuple)):
        params[param_key] = formatter(value[0])
        params[f"{param_key}_2"] = formatter(value[1])
        return f"{field} BETWEEN :{param_key} AND {param_key}_2"

    params[param_key] = formatter(value)
    return f"{field} = :{param_key}"


def filter_values(
    field: str,
    values: Sequence[Union[Tuple[str, str], str, Tuple[int, int], int]],
    param_key: str,
    params: Dict[str, Any],
    formatter=lambda x: x,
):
    # builds a SQL expression to filter strings (ex: locations)
    #   $field: name of the field to filter
    #   $values: array of values
    conditions = [
        to_condition(field, v, f"{param_key}_{i}", params, formatter)
        for i, v in enumerate(values)
    ]
    return f"({' OR '.join(conditions)})"


def filter_strings(
    field: str,
    values: Sequence[Union[Tuple[str, str], str]],
    param_key: str,
    params: Dict[str, Any],
):
    return filter_values(field, values, param_key, params)


def filter_integers(
    field: str,
    values: Sequence[Union[Tuple[int, int], int]],
    param_key: str,
    params: Dict[str, Any],
):
    return filter_values(field, values, param_key, params)


def filter_dates(
    field: str,
    values: Sequence[Union[Tuple[int, int], int]],
    param_key: str,
    params: Dict[str, Any],
):
    return filter_values(field, values, param_key, params, date_string)


def execute_query(
    query: str,
    params: Dict[str, Any],
    fields_string: Sequence[str],
    fields_int: Sequence[str],
    fields_float: Sequence[str],
):
    p = create_printer()

    fields_to_send = set(extract_strings("fields") or [])
    if fields_to_send:
        fields_string = [v for v in fields_string if v in fields_to_send]
        fields_int = [v for v in fields_int if v in fields_to_send]
        fields_float = [v for v in fields_float if v in fields_to_send]

    def gen():
        r = db.execute(text(query), **params)

        for row in r:
            filtered = dict()
            for f in fields_string:
                filtered[f] = row.get(f)
            for f in fields_int:
                filtered[f] = int(row.get(f)) if f in row else None
            for f in fields_float:
                filtered[f] = float(row.get(f)) if f in row else None
            yield filtered

    return p(gen)
