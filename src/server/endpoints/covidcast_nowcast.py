from flask import Blueprint, request

from .._params import (
    extract_date,
    extract_dates,
    extract_integer,
    extract_strings
)
from .._query import execute_query, filter_integers, filter_strings
from .._validate import (
    require_all,
    require_any,
)

# first argument is the endpoint name
bp = Blueprint("covidcast_nowcast", __name__)
alias = None


@bp.route("/", methods=("GET", "POST"))
def handle():
    require_all(
        request, "data_source", "time_type", "geo_type", "time_values", "signals", "sensor_names"
    )
    require_any(request, "geo_value", "geo_values", empty=True)

    time_values = extract_dates("time_values")
    as_of = extract_date("as_of")
    issues = extract_dates("issues")
    lag = extract_integer("lag")
    signals = extract_strings(("signals", "signal"))
    sensor_names = extract_strings("sensor_names")
    geo_values = extract_strings(("geo_values", "geo_value"))
    data_source = request.values["data_source"]
    time_type = request.values["time_type"]
    geo_type = request.values["geo_type"]

    # build query
    table = "`covidcast_nowcast` t"
    fields = "t.`signal`, t.`time_value`, t.`geo_value`, t.`value`, t.`issue`, t.`lag`"
    order = "t.`signal` ASC, t.`time_value` ASC, t.`geo_value` ASC, t.`issue` ASC"

    params = dict()
    # basic query info
    # data type of each field
    # build the source, signal, time, and location (type and id) filters
    condition_source = "t.`source` = :source"
    params["source"] = data_source
    condition_signal = filter_strings("t.`signal`", signals, "signal", params)
    condition_sensor_name = filter_strings(
        "t.`sensor_name`", sensor_names, "sensor_name", params
    )
    condition_time_type = "t.`time_type` = :time_type"
    params["time_type"] = time_type
    condition_geo_type = "t.`geo_type` = :geo_type"
    params["geo_type"] = geo_type
    condition_time_value = filter_integers(
        "t.`time_value`", time_values, "time_value", params
    )

    if not geo_values:
        condition_geo_value = "FALSE"
    elif len(geo_values) == 1 and geo_values[0] == "*":
        # the wildcard query should return data for all locations in `geo_type`
        condition_geo_value = "TRUE"
    else:
        # return data for multiple location
        condition_geo_value = filter_strings(
            "t.`geo_value`", geo_values, "geo_value", params
        )

    conditions = f"({condition_source}) AND ({condition_signal}) AND ({condition_sensor_name}) AND ({condition_time_type}) AND ({condition_geo_type}) AND ({condition_time_value}) AND ({condition_geo_value})"

    subquery = ""
    if issues:
        # build the issue filter
        condition_issue = filter_integers("t.`issue`", issues, "issue", params)
        query = f"SELECT {fields} FROM {table} {subquery} WHERE {conditions} AND ({condition_issue}) ORDER BY {order}"
    elif lag:
        # build the lag filter
        condition_lag = "(t.`lag` = :lag)"
        params["lag"] = lag
        query = f"SELECT {fields} FROM {table} {subquery} WHERE {conditions} AND ({condition_lag}) ORDER BY {order}"
    elif as_of:
        # fetch most recent issues with as of
        sub_condition_asof = "(`issue` <= :as_of)"
        params["as_of"] = as_of
        sub_fields = "max(`issue`) `max_issue`, `time_type`, `time_value`, `source`, `signal`, `geo_type`, `geo_value`"
        sub_group = (
            "`time_type`, `time_value`, `source`, `signal`, `geo_type`, `geo_value`"
        )
        sub_condition = "x.`max_issue` = t.`issue` AND x.`time_type` = t.`time_type` AND x.`time_value` = t.`time_value` AND x.`source` = t.`source` AND x.`signal` = t.`signal` AND x.`geo_type` = t.`geo_type` AND x.`geo_value` = t.`geo_value`"
        subquery = f"JOIN (SELECT {sub_fields} FROM {table} WHERE ({conditions} AND {sub_condition_asof}) GROUP BY {sub_group}) x ON {sub_condition}"
        condition_version = "TRUE"
        query = f"SELECT {fields} FROM {table} {subquery} WHERE {conditions} AND ({condition_version}) ORDER BY {order}"
    else:
        # fetch most recent issue fast
        query = f"WITH t as (SELECT {fields}, ROW_NUMBER() OVER (PARTITION BY t.`time_type`, t.`time_value`, t.`source`, t.`signal`, t.`geo_type`, t.`geo_value` ORDER BY t.`issue` DESC) `row` FROM {table}  {subquery} WHERE {conditions}) SELECT {fields} FROM t where `row` = 1 ORDER BY {order}"

    fields_string = ["geo_value", "signal"]
    fields_int = ["time_value", "issue", "lag"]
    fields_float = ["value"]

    # send query
    return execute_query(query, params, fields_string, fields_int, fields_float)
