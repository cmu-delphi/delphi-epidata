from datetime import date, datetime
from typing import (
    Any,
    Dict,
    Iterable,
    List,
    Optional,
    Sequence,
    Tuple,
    Union,
    cast,
    Mapping,
)

from sqlalchemy import text
from sqlalchemy.engine import RowProxy

from ._common import db, app
from ._db import metadata
from ._printer import create_printer
from ._validate import DateRange, extract_strings


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
) -> str:
    if isinstance(value, (list, tuple)):
        params[param_key] = formatter(value[0])
        params[f"{param_key}_2"] = formatter(value[1])
        return f"{field} BETWEEN :{param_key} AND :{param_key}_2"

    params[param_key] = formatter(value)
    return f"{field} = :{param_key}"


def filter_values(
    field: str,
    values: Optional[Sequence[Union[Tuple[str, str], str, Tuple[int, int], int]]],
    param_key: str,
    params: Dict[str, Any],
    formatter=lambda x: x,
):
    if not values:
        return "FALSE"
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
    values: Optional[Sequence[Union[Tuple[str, str], str]]],
    param_key: str,
    params: Dict[str, Any],
):
    return filter_values(field, values, param_key, params)


def filter_integers(
    field: str,
    values: Optional[Sequence[Union[Tuple[int, int], int]]],
    param_key: str,
    params: Dict[str, Any],
):
    return filter_values(field, values, param_key, params)


def filter_dates(
    field: str,
    values: Optional[Sequence[Union[Tuple[int, int], int]]],
    param_key: str,
    params: Dict[str, Any],
):
    return filter_values(field, values, param_key, params, date_string)


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


def parse_row(
    row: RowProxy,
    fields_string: Optional[Sequence[str]] = None,
    fields_int: Optional[Sequence[str]] = None,
    fields_float: Optional[Sequence[str]] = None,
):
    keys = set(row.keys())
    parsed = dict()
    if fields_string:
        for f in fields_string:
            v = row[f] if f in keys else None
            if isinstance(v, (date, datetime)):
                v = v.strftime("%Y-%m-%d")  # format to iso date
            parsed[f] = v
    if fields_int:
        for f in fields_int:
            parsed[f] = int(row[f]) if f in keys and row[f] is not None else None
    if fields_float:
        for f in fields_float:
            parsed[f] = float(row[f]) if f in keys and row[f] is not None else None
    return parsed


def parse_result(
    query: str,
    params: Dict[str, Any],
    fields_string: Optional[Sequence[str]] = None,
    fields_int: Optional[Sequence[str]] = None,
    fields_float: Optional[Sequence[str]] = None,
) -> List[Dict[str, Any]]:
    """
    execute the given query and return the result as a list of dictionaries
    """
    return [
        parse_row(row, fields_string, fields_int, fields_float)
        for row in db.execute(text(query), **params)
    ]


def execute_queries(
    queries: Sequence[Tuple[str, Dict[str, Any]]],
    fields_string: Sequence[str],
    fields_int: Sequence[str],
    fields_float: Sequence[str],
):
    """
    execute the given queries and return the response to send them
    """
    p = create_printer()

    fields_to_send = set(extract_strings("fields") or [])
    if fields_to_send:
        fields_string = [v for v in fields_string if v in fields_to_send]
        fields_int = [v for v in fields_int if v in fields_to_send]
        fields_float = [v for v in fields_float if v in fields_to_send]

    def gen():
        for query, params in queries:
            if p.remaining_rows <= 0:
                # no more rows
                break
            # limit rows + 1 for detecting whether we would have more
            full_query = text(f"{query} LIMIT {p.remaining_rows + 1}")
            app.logger.info("full_query: %s, params: %s", full_query, params)
            r = db.execution_options(stream_results=True).execute(full_query, **params)
            for row in r:
                yield parse_row(row, fields_string, fields_int, fields_float)

    return p(gen())


def execute_query(
    query: str,
    params: Dict[str, Any],
    fields_string: Sequence[str],
    fields_int: Sequence[str],
    fields_float: Sequence[str],
):
    """
    execute the given query and return the response to send it
    """
    return execute_queries([(query, params)], fields_string, fields_int, fields_float)


def join_l(value: Union[str, List[str]]):
    return ", ".join(value) if isinstance(value, (list, tuple)) else value


class QueryBuilder:
    """
    query builder helper class for simplified conditions
    """

    def __init__(self, table: str, alias: str):
        self.table: str = f"{table} {alias}"
        self.alias: str = alias
        self.group_by: Union[str, List[str]] = ""
        self.order: Union[str, List[str]] = ""
        self.fields: Union[str, List[str]] = "*"
        self.conditions: List[str] = []
        self.params: Dict[str, Any] = {}
        self.subquery: str = ""

    @property
    def conditions_clause(self) -> str:
        return " AND ".join(self.conditions)

    @property
    def fields_clause(self) -> str:
        return join_l(self.fields) if self.fields else "*"

    def __str__(self):
        where = f"WHERE {self.conditions_clause}" if self.conditions else ""
        order = f"ORDER BY {join_l(self.order)}" if self.order else ""
        group_by = f"GROUP BY {join_l(self.group_by)}" if self.group_by else ""

        return f"SELECT {self.fields_clause} FROM {self.table} {self.subquery} {where} {group_by} {order}"

    def where(self, **kvargs: Dict[str, Any]) -> "QueryBuilder":
        for k, v in kvargs.items():
            self.conditions.append(f"{self.alias}.{k} = :{k}")
            self.params[k] = v
        return self

    def where_strings(
        self,
        field: str,
        values: Optional[Sequence[Union[Tuple[str, str], str]]],
        param_key: Optional[str] = None,
    ) -> "QueryBuilder":
        fq_field = f"{self.alias}.{field}" if "." not in field else field
        self.conditions.append(
            filter_strings(fq_field, values, param_key or field, self.params)
        )
        return self

    def where_integers(
        self,
        field: str,
        values: Optional[Sequence[Union[Tuple[int, int], int]]],
        param_key: Optional[str] = None,
    ) -> "QueryBuilder":
        fq_field = f"{self.alias}.{field}" if "." not in field else field
        self.conditions.append(
            filter_integers(fq_field, values, param_key or field, self.params)
        )
        return self

    def where_dates(
        self,
        field: str,
        values: Optional[Sequence[Union[Tuple[int, int], int]]],
        param_key: Optional[str] = None,
    ) -> "QueryBuilder":
        fq_field = f"{self.alias}.{field}" if "." not in field else field
        self.conditions.append(
            filter_dates(fq_field, values, param_key or field, self.params)
        )
        return self

    def set_fields(self, *fields: Iterable[str]) -> "QueryBuilder":
        self.fields = [
            f"{self.alias}.{field}" for field_list in fields for field in field_list
        ]
        return self

    def set_order(self, *args: str, **kwargs: Union[str, bool]) -> "QueryBuilder":
        """
        sets the order for the given fields (as key word arguments), True = ASC, False = DESC
        """

        def to_asc(v: Union[str, bool]) -> str:
            if v == True:
                return "ASC"
            elif v == False:
                return "DESC"
            return cast(str, v)

        args_order = [f"{self.alias}.{k} ASC" for k in args]
        kw_order = [f"{self.alias}.{k} {to_asc(v)}" for k, v in kwargs.items()]
        self.order = args_order + kw_order
        return self

    def with_max_issue(self, *args: str) -> "QueryBuilder":
        fields: List[str] = [f for f in args]

        subfields = f"max(issue) max_issue, {','.join(fields)}"
        group_by = ",".join(fields)
        field_conditions = " AND ".join(
            f"x.{field} = {self.alias}.{field}" for field in fields
        )
        condition = f"x.max_issue = {self.alias}.issue AND {field_conditions}"
        self.subquery = f"JOIN (SELECT {subfields} FROM {self.table} WHERE {self.conditions_clause} GROUP BY {group_by}) x ON {condition}"
        # reset conditions since for join
        self.conditions = []
        return self
