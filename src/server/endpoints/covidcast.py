from flask import Blueprint, request
from typing import List

from .._query import execute_query, filter_integers, filter_strings, QueryBuilder
from .._validate import (
    extract_date,
    extract_dates,
    extract_integer,
    extract_integers,
    extract_strings,
    require_all,
    require_any,
)

# first argument is the endpoint name
bp = Blueprint("covidcast", __name__)
alias = None

def where_geo_values(q: QueryBuilder, geo_values: List[str]):
    if not geo_values:
        q.conditions.append("FALSE")
    elif len(geo_values) == 1 and geo_values[0] == "*":
        # the wildcard query should return data for all locations in geo_type
        pass
    else:
        # return data for multiple location
        q.where_strings("geo_value", geo_values)


@bp.route("/", methods=("GET", "POST"))
def handle():
    require_all("data_source", "time_type", "geo_type", "time_values")
    require_any("signal", "signals")
    require_any("geo_value", "geo_values", empty=True)

    time_values = extract_dates("time_values")
    as_of = extract_date("as_of")
    issues = extract_dates("issues")
    lag = extract_integer("lag")
    signals = extract_strings(("signals", "signal"))
    geo_values = extract_strings(("geo_values", "geo_value"))
    data_source = request.values["data_source"]
    time_type = request.values["time_type"]
    geo_type = request.values["geo_type"]

    # build query
    q = QueryBuilder("covidcast", "t")

    fields_string = ["geo_value", "signal"]
    fields_int = ["time_value", "direction", "issue", "lag"]
    fields_float = ["value", "stderr", "sample_size"]
    q.set_fields(fields_string, fields_int, fields_float)
    q.set_order('signal', 'time_value', 'geo_value', 'issue')

    # basic query info
    # data type of each field
    # build the source, signal, time, and location (type and id) filters

    q.where(source=data_source, time_type=time_type, geo_type=geo_type)
    q.where_strings("signal", signals)
    q.where_integers("time_value", time_values)

    where_geo_values(q, geo_values)

    subquery = ""
    if issues:
        q.where_integers("issue", issues)
    elif lag:
        q.where(lag=lag)
    elif as_of:
        # fetch most recent issues with as of
        sub_condition_asof = "(issue <= :as_of)"
        q.params["as_of"] = as_of
        sub_fields = "max(issue) max_issue, time_type, time_value, `source`, `signal`, geo_type, geo_value"
        sub_group = "time_type, time_value, `source`, `signal`, geo_type, geo_value"
        sub_condition = f"x.max_issue = {q.alias}.issue AND x.time_type = {q.alias}.time_type AND x.time_value = {q.alias}.time_value AND x.source = {q.alias}.source AND x.signal = {q.alias}.signal AND x.geo_type = {q.alias}.geo_type AND x.geo_value = {q.alias}.geo_value"
        q.subquery = f"JOIN (SELECT {sub_fields} FROM {q.table} WHERE {q.conditions_clause} AND {sub_condition_asof} GROUP BY {sub_group}) x ON {sub_condition}"
        # condition_version = "TRUE"
    else:
        # fetch most recent issue fast
        q.conditions.append(f"({q.alias}.is_latest_issue IS TRUE)")

    # send query
    return execute_query(str(q), q.params, fields_string, fields_int, fields_float)
