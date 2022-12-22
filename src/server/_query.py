from datetime import date, datetime
from typing import (
    Any,
    Callable,
    Dict,
    Iterable,
    List,
    Optional,
    Sequence,
    Tuple,
    Union,
    cast
)

from sqlalchemy import text
from sqlalchemy.engine import Row

from ._common import db
from ._printer import create_printer, APrinter
from ._exceptions import DatabaseErrorException
from ._validate import extract_strings
from ._params import GeoPair, SourceSignalPair, TimePair
from .utils import time_values_to_ranges, TimeValues


def date_string(value: int) -> str:
    # converts a date integer (YYYYMMDD) into a date string (YYYY-MM-DD)
    # $value: the date as an 8-digit integer
    year = int(value / 10000) % 10000
    month = int(value / 100) % 100
    day = value % 100
    return "{0:04d}-{1:02d}-{2:02d}".format(year, month, day)


def to_condition(
    field: str,
    value: Union[str, Tuple[int, int], int],
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
    values: Optional[Sequence[Union[str, Tuple[int, int], int]]],
    param_key: str,
    params: Dict[str, Any],
    formatter=lambda x: x,
):
    if not values:
        return "FALSE"
    # builds a SQL expression to filter strings (ex: locations)
    #   $field: name of the field to filter
    #   $values: array of values
    conditions = [to_condition(field, v, f"{param_key}_{i}", params, formatter) for i, v in enumerate(values)]
    return f"({' OR '.join(conditions)})"


def filter_strings(
    field: str,
    values: Optional[Sequence[str]],
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
    values: Optional[TimeValues],
    param_key: str,
    params: Dict[str, Any],
):
    ranges = time_values_to_ranges(values)
    return filter_values(field, ranges, param_key, params, date_string)


def filter_fields(generator: Iterable[Dict[str, Any]]):
    fields = extract_strings("fields")
    if not fields:
        yield from generator
    else:
        exclude_fields = {f[1:] for f in fields if f.startswith("-")}
        include_fields = [f for f in fields if not f.startswith("-") and f not in exclude_fields]

        for row in generator:
            filtered = dict()
            if include_fields:
                # positive list
                for field in include_fields:
                    if field in row:
                        filtered[field] = row[field]
            elif exclude_fields:
                # negative list
                for k, v in row.items():
                    if k not in exclude_fields:
                        filtered[k] = v
            yield filtered


def filter_geo_pairs(
    type_field: str,
    value_field: str,
    values: Sequence[GeoPair],
    param_key: str,
    params: Dict[str, Any],
) -> str:
    """
    returns the SQL sub query to filter by the given geo pairs
    """

    def filter_pair(pair: GeoPair, i) -> str:
        type_param = f"{param_key}_{i}t"
        params[type_param] = pair.geo_type
        if isinstance(pair.geo_values, bool) and pair.geo_values:
            return f"{type_field} = :{type_param}"
        return f"({type_field} = :{type_param} AND {filter_strings(value_field, cast(Sequence[str], pair.geo_values), type_param, params)})"

    parts = [filter_pair(p, i) for i, p in enumerate(values)]

    if not parts:
        # something has to be selected
        return "FALSE"

    return f"({' OR '.join(parts)})"


def filter_source_signal_pairs(
    source_field: str,
    signal_field: str,
    values: Sequence[SourceSignalPair],
    param_key: str,
    params: Dict[str, Any],
) -> str:
    """
    returns the SQL sub query to filter by the given source signal pairs
    """

    def filter_pair(pair: SourceSignalPair, i) -> str:
        source_param = f"{param_key}_{i}t"
        params[source_param] = pair.source
        if isinstance(pair.signal, bool) and pair.signal:
            return f"{source_field} = :{source_param}"
        return f"({source_field} = :{source_param} AND {filter_strings(signal_field, cast(Sequence[str], pair.signal), source_param, params)})"

    parts = [filter_pair(p, i) for i, p in enumerate(values)]

    if not parts:
        # something has to be selected
        return "FALSE"

    return f"({' OR '.join(parts)})"


def filter_time_pair(
    type_field: str,
    time_field: str,
    pair: Optional[TimePair],
    param_key: str,
    params: Dict[str, Any],
) -> str:
    """
    returns the SQL sub query to filter by the given time pair
    """
    # safety path; should normally not be reached as time pairs are enforced by the API
    if not pair:
        return "FALSE"

    type_param = f"{param_key}_0t"
    params[type_param] = pair.time_type
    if isinstance(pair.time_values, bool) and pair.time_values:
        parts =  f"{type_field} = :{type_param}"
    else:
        ranges = pair.to_ranges().time_values
        parts = f"({type_field} = :{type_param} AND {filter_integers(time_field, ranges, type_param, params)})"

    return f"({parts})"


def parse_row(
    row: Row,
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
    return [parse_row(row, fields_string, fields_int, fields_float) for row in db.execute(text(query), **params)]


def limit_query(query: str, limit: int) -> str:
    full_query = f"{query} LIMIT {limit}"
    return full_query


def run_query(p: APrinter, query_tuple: Tuple[str, Dict[str, Any]]):
    query, params = query_tuple
    # limit rows + 1 for detecting whether we would have more
    full_query = text(limit_query(query, p.remaining_rows + 1))
    return db.execution_options(stream_results=True).execute(full_query, **params)


def _identity_transform(row: Dict[str, Any], _: Row) -> Dict[str, Any]:
    """
    identity transform
    """
    return row


def execute_queries(
    queries: Sequence[Tuple[str, Dict[str, Any]]],
    fields_string: Sequence[str],
    fields_int: Sequence[str],
    fields_float: Sequence[str],
    transform: Callable[[Dict[str, Any], Row], Dict[str, Any]] = _identity_transform,
):
    """
    execute the given queries and return the response to send them
    """

    p = create_printer()

    fields_to_send = set(extract_strings("fields") or [])
    if fields_to_send:
        exclude_fields = {f[1:] for f in fields_to_send if f.startswith("-")}
        include_fields = {f for f in fields_to_send if not f.startswith("-") and f not in exclude_fields}

        if include_fields:
            fields_string = [v for v in fields_string if v in include_fields]
            fields_int = [v for v in fields_int if v in include_fields]
            fields_float = [v for v in fields_float if v in include_fields]
        if exclude_fields:
            fields_string = [v for v in fields_string if v not in exclude_fields]
            fields_int = [v for v in fields_int if v not in exclude_fields]
            fields_float = [v for v in fields_float if v not in exclude_fields]

    query_list = list(queries)

    def dummy_gen():
        if 3 > 4:
            yield {}

    if not query_list or p.remaining_rows <= 0:
        return p(dummy_gen)

    def gen(first_rows):
        for row in first_rows:
            yield transform(parse_row(row, fields_string, fields_int, fields_float), row)

        for query_params in query_list:
            if p.remaining_rows <= 0:
                # no more rows
                break
            r = run_query(p, query_params)
            for row in r:
                yield transform(parse_row(row, fields_string, fields_int, fields_float), row)

    # execute first query
    try:
        r = run_query(p, query_list.pop(0))
    except Exception as e:
        raise DatabaseErrorException(str(e))

    # now use a generator for sending the rows and execute all the other queries
    return p(gen(r))


def execute_query(
    query: str,
    params: Dict[str, Any],
    fields_string: Sequence[str],
    fields_int: Sequence[str],
    fields_float: Sequence[str],
    transform: Callable[[Dict[str, Any], Row], Dict[str, Any]] = _identity_transform,
):
    """
    execute the given query and return the response to send it
    """
    return execute_queries([(query, params)], fields_string, fields_int, fields_float, transform)


def _join_l(value: Union[str, List[str]]):
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
        self.index: Optional[str] = None

    def retable(self, new_table: str):
        """
        updates this QueryBuilder to point to another table.
        useful for switching to a different view of the data...
        """
        # WARNING: if we ever switch to re-using QueryBuilder, we should change this to return a copy.
        self.table: str = f"{new_table} {self.alias}"
        return self

    @property
    def conditions_clause(self) -> str:
        return " AND ".join(self.conditions)

    @property
    def fields_clause(self) -> str:
        return _join_l(self.fields) if self.fields else "*"

    @property
    def order_clause(self) -> str:
        return _join_l(self.order)

    def __str__(self):
        where = f"WHERE {self.conditions_clause}" if self.conditions else ""
        order = f"ORDER BY {_join_l(self.order)}" if self.order else ""
        group_by = f"GROUP BY {_join_l(self.group_by)}" if self.group_by else ""
        index = f"USE INDEX ({self.index})" if self.index else ""

        return f"SELECT {self.fields_clause} FROM {self.table} {index} {self.subquery} {where} {group_by} {order}"

    @property
    def query(self) -> str:
        """
        returns the full query
        """
        return str(self)

    def where(self, **kvargs: Dict[str, Any]) -> "QueryBuilder":
        for k, v in kvargs.items():
            self.conditions.append(f"{self.alias}.{k} = :{k}")
            self.params[k] = v
        return self

    def where_strings(
        self,
        field: str,
        values: Optional[Sequence[str]],
        param_key: Optional[str] = None,
    ) -> "QueryBuilder":
        fq_field = f"{self.alias}.{field}" if "." not in field else field
        self.conditions.append(filter_strings(fq_field, values, param_key or field, self.params))
        return self

    def _fq_field(self, field: str) -> str:
        return f"{self.alias}.{field}" if "." not in field else field

    def where_integers(
        self,
        field: str,
        values: Optional[Sequence[Union[Tuple[int, int], int]]],
        param_key: Optional[str] = None,
    ) -> "QueryBuilder":
        fq_field = self._fq_field(field)
        self.conditions.append(filter_integers(fq_field, values, param_key or field, self.params))
        return self

    def where_geo_pairs(
        self,
        type_field: str,
        value_field: str,
        values: Sequence[GeoPair],
        param_key: Optional[str] = None,
    ) -> "QueryBuilder":
        fq_type_field = self._fq_field(type_field)
        fq_value_field = self._fq_field(value_field)
        self.conditions.append(
            filter_geo_pairs(
                fq_type_field,
                fq_value_field,
                values,
                param_key or type_field,
                self.params,
            )
        )
        return self

    def where_source_signal_pairs(
        self,
        type_field: str,
        value_field: str,
        values: Sequence[SourceSignalPair],
        param_key: Optional[str] = None,
    ) -> "QueryBuilder":
        fq_type_field = self._fq_field(type_field)
        fq_value_field = self._fq_field(value_field)
        self.conditions.append(
            filter_source_signal_pairs(
                fq_type_field,
                fq_value_field,
                values,
                param_key or type_field,
                self.params,
            )
        )
        return self

    def where_time_pair(
        self,
        type_field: str,
        value_field: str,
        values: Optional[TimePair],
        param_key: Optional[str] = None,
    ) -> "QueryBuilder":
        fq_type_field = self._fq_field(type_field)
        fq_value_field = self._fq_field(value_field)
        self.conditions.append(
            filter_time_pair(
                fq_type_field,
                fq_value_field,
                values,
                param_key or type_field,
                self.params,
            )
        )
        return self

    def apply_lag_filter(self, history_table: str, lag: Optional[int]):
        if lag is not None:
            self.retable(history_table)
            # history_table has full spectrum of lag values to search from whereas the latest_table does not
            self.where(lag=lag)

    def apply_issues_filter(self, history_table: str, issues: Optional[TimeValues]):
        if issues:
            self.retable(history_table)
            self.where_integers("issue", issues)

    def apply_as_of_filter(self, history_table: str, as_of: Optional[int]):
        if as_of is not None:
            self.retable(history_table)
            sub_condition_asof = "(issue <= :as_of)"
            self.params["as_of"] = as_of
            sub_fields = "max(issue) max_issue, time_type, time_value, `source`, `signal`, geo_type, geo_value"
            sub_group = "time_type, time_value, `source`, `signal`, geo_type, geo_value"
            sub_condition = f"x.max_issue = {self.alias}.issue AND x.time_type = {self.alias}.time_type AND x.time_value = {self.alias}.time_value AND x.source = {self.alias}.source AND x.signal = {self.alias}.signal AND x.geo_type = {self.alias}.geo_type AND x.geo_value = {self.alias}.geo_value"
            self.subquery = f"JOIN (SELECT {sub_fields} FROM {self.table} WHERE {self.conditions_clause} AND {sub_condition_asof} GROUP BY {sub_group}) x ON {sub_condition}"

    def set_fields(self, *fields: Iterable[str]) -> "QueryBuilder":
        self.fields = [f"{self.alias}.{field}" for field_list in fields for field in field_list]
        return self

    def set_sort_order(self, *args: str):
        """
        sets the order for the given fields (as key word arguments), True = ASC, False = DESC
        """

        self.order = [f"{self.alias}.{k} ASC" for k in args]

    def with_max_issue(self, *args: str) -> "QueryBuilder":
        fields: List[str] = [f for f in args]

        subfields = f"max(issue) max_issue, {','.join(fields)}"
        group_by = ",".join(fields)
        field_conditions = " AND ".join(f"x.{field} = {self.alias}.{field}" for field in fields)
        condition = f"x.max_issue = {self.alias}.issue AND {field_conditions}"
        self.subquery = f"JOIN (SELECT {subfields} FROM {self.table} WHERE {self.conditions_clause} GROUP BY {group_by}) x ON {condition}"
        # reset conditions since for join
        self.conditions = []
        return self
