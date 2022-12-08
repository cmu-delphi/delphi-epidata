from typing import List, Optional, Tuple, Dict, Any
from itertools import groupby
from datetime import date, timedelta
from bisect import bisect_right
from epiweeks import Week
from flask import Blueprint, request, Response
from flask.json import loads, jsonify
from more_itertools import peekable
from numpy import nan
from sqlalchemy import text
from pandas import read_csv, to_datetime
from numbers import Number

from .._common import is_compatibility_mode, app, db
from .._config import MAX_SMOOTHER_WINDOW, MAX_RESULTS
from .._exceptions import ValidationFailedException, DatabaseErrorException, TransformErrorException
from .._params import (
    GeoPair,
    SourceSignalPair,
    TimePair,
    parse_geo_arg,
    parse_source_signal_arg,
    parse_time_arg,
    parse_day_or_week_arg,
    parse_day_or_week_range_arg,
    parse_single_source_signal_arg,
    parse_single_time_arg,
    parse_single_geo_arg,
)
from .._query import QueryBuilder, execute_query, run_query, parse_row, filter_fields
from .._printer import create_printer, CSVPrinter
from .._validate import (
    extract_bool,
    extract_date,
    extract_dates,
    extract_integer,
    extract_float,
    extract_strings,
    require_all,
    require_any,
)
from .._pandas import as_pandas, print_pandas
from .covidcast_utils import compute_trend, compute_trends, compute_correlations, compute_trend_value, CovidcastMetaEntry
from ..utils import shift_day_value, day_to_time_value, time_value_to_iso, time_value_to_day, shift_week_value, time_value_to_week, guess_time_value_is_day, week_to_time_value, TimeValues
from .covidcast_utils.model import TimeType, count_signal_time_types, data_sources, data_sources_by_id, create_source_signal_alias_mapper, get_pad_length, pad_time_pair, pad_time_window, get_basename_signals_and_derived_map, generate_transformed_rows, generate_transformed_rows3

# first argument is the endpoint name
bp = Blueprint("covidcast", __name__)
alias = None
JIT_COMPUTE_ON = True

latest_table = "epimetric_latest_v"
history_table = "epimetric_full_v"

def parse_source_signal_pairs() -> List[SourceSignalPair]:
    ds = request.values.get("data_source")
    if ds:
        # old version
        require_any("signal", "signals", empty=True)
        signals = extract_strings(("signals", "signal"))
        if len(signals) == 1 and signals[0] == "*":
            return [SourceSignalPair(ds, True)]
        return [SourceSignalPair(ds, signals)]

    if ":" not in request.values.get("signal", ""):
        raise ValidationFailedException("missing parameter: signal or (data_source and signal[s])")

    # Convert source_signal_pairs with signal == True out to an explicit list of signals.
    expanded_bool_source_signal_pairs = []
    for source_signal_pair in parse_source_signal_arg():
        if source_signal_pair.signal is True:
            if data_source := data_sources_by_id.get(source_signal_pair.source):
                expanded_bool_source_signal_pairs.append(SourceSignalPair(data_source.source, [s.signal for s in data_source.signals]))
            else:
                expanded_bool_source_signal_pairs.append(source_signal_pair)
        else:
            expanded_bool_source_signal_pairs.append(source_signal_pair)

    return expanded_bool_source_signal_pairs


def parse_geo_pairs() -> List[GeoPair]:
    geo_type = request.values.get("geo_type")
    if geo_type:
        # old version
        require_any("geo_value", "geo_values", empty=True)
        geo_values = extract_strings(("geo_values", "geo_value"))
        if len(geo_values) == 1 and geo_values[0] == "*":
            return [GeoPair(geo_type, True)]
        return [GeoPair(geo_type, geo_values)]

    if ":" not in request.values.get("geo", ""):
        raise ValidationFailedException("missing parameter: geo or (geo_type and geo_value[s])")

    return parse_geo_arg()


def parse_time_pair() -> TimePair:
    time_type = request.values.get("time_type")
    if time_type:
        # old version
        require_all("time_type", "time_values")
        time_values = extract_dates("time_values")
        return TimePair(time_type, time_values)

    if ":" not in request.values.get("time", ""):
        raise ValidationFailedException("missing parameter: time or (time_type and time_values)")

    time_pair = parse_time_arg()
    return time_pair


def _handle_lag_issues_as_of(q: QueryBuilder, issues: Optional[TimeValues] = None, lag: Optional[int] = None, as_of: Optional[int] = None):
    if issues:
        q.retable(history_table)
        q.where_integers("issue", issues)
    elif lag is not None:
        q.retable(history_table)
        # history_table has full spectrum of lag values to search from whereas the latest_table does not
        q.where(lag=lag)
    elif as_of is not None:
        # fetch the most recent issue as of a certain date (not to be confused w/ plain-old "most recent issue"
        q.retable(history_table)
        sub_condition_asof = "(issue <= :as_of)"
        q.params["as_of"] = as_of
        sub_fields = "max(issue) max_issue, time_type, time_value, `source`, `signal`, geo_type, geo_value"
        sub_group = "time_type, time_value, `source`, `signal`, geo_type, geo_value"
        sub_condition = f"x.max_issue = {q.alias}.issue AND x.time_type = {q.alias}.time_type AND x.time_value = {q.alias}.time_value AND x.source = {q.alias}.source AND x.signal = {q.alias}.signal AND x.geo_type = {q.alias}.geo_type AND x.geo_value = {q.alias}.geo_value"
        q.subquery = f"JOIN (SELECT {sub_fields} FROM {q.table} WHERE {q.conditions_clause} AND {sub_condition_asof} GROUP BY {sub_group}) x ON {sub_condition}"
    else:
        # else we are using the (standard/default) `latest_table`, to fetch the most recent issue quickly
        pass


def parse_transform_args():
    # The length of the window to smooth over.
    smoother_window_length = extract_integer("smoother_window_length")
    if smoother_window_length is None:
        smoother_window_length = 7
    elif not isinstance(smoother_window_length, int):
        raise ValidationFailedException("smoother_window_length must be an integer")
    elif smoother_window_length > MAX_SMOOTHER_WINDOW:
        raise ValidationFailedException(f"smoother_window_length must be <= {MAX_SMOOTHER_WINDOW}")

    # The value to fill for missing date values.
    pad_fill_value = extract_float("pad_fill_value")
    if pad_fill_value is None:
        pad_fill_value = nan
    elif not isinstance(pad_fill_value, Number):
        raise ValidationFailedException("pad_fill_value must be a number")

    # The value to fill for None or nan values.
    nan_fill_value = extract_float("nans_fill_value")
    if nan_fill_value is None:
        nan_fill_value = nan
    elif not isinstance(nan_fill_value, Number):
        raise ValidationFailedException("nans_fill_value must be a number")

    smoother_args = {
        "smoother_window_length": smoother_window_length,
        "pad_fill_value": pad_fill_value,
        "nans_fill_value": nan_fill_value,
    }
    return smoother_args


def parse_jit_bypass():
    jit_bypass = extract_bool("jit_bypass")
    if jit_bypass is None:
        return False
    else:
        return jit_bypass


@bp.route("/", methods=("GET", "POST"))
def handle():
    source_signal_pairs = parse_source_signal_pairs()
    source_signal_pairs, alias_mapper = create_source_signal_alias_mapper(source_signal_pairs)
    time_pair = parse_time_pair()
    geo_pairs = parse_geo_pairs()
    jit_bypass = parse_jit_bypass()

    as_of = extract_date("as_of")
    issues = extract_dates("issues")
    lag = extract_integer("lag")
    is_time_type_week = time_pair.time_type == "week"

    is_compatibility = is_compatibility_mode()
    def alias_row(row):
        if is_compatibility:
            # old api returned fewer fields
            remove_fields = ["geo_type", "source", "time_type"]
            for field in remove_fields:
                if field in row:
                    del row[field]
        if is_compatibility or not alias_mapper or "source" not in row:
            return row
        row["source"] = alias_mapper(row["source"], row["signal"])
        return row

    # build query
    q = QueryBuilder(latest_table, "t")

    fields_string = ["geo_type", "geo_value", "source", "signal", "time_type"]
    fields_int = ["time_value", "direction", "issue", "lag", "missing_value", "missing_stderr", "missing_sample_size"]
    fields_float = ["value", "stderr", "sample_size"]

    use_jit_compute = not any((issues, lag, is_time_type_week)) and JIT_COMPUTE_ON and not jit_bypass
    if use_jit_compute:
        transform_args = parse_transform_args()
        pad_length = get_pad_length(source_signal_pairs, transform_args.get("smoother_window_length"))
        time_pair = pad_time_pair(time_pair, pad_length)
        app.logger.info(f"JIT compute enabled for route '/': {source_signal_pairs}")
        source_signal_pairs, derived_signals_map = get_basename_signals_and_derived_map(source_signal_pairs)
        app.logger.info(f"JIT base signals: {source_signal_pairs}")

        q.set_order("source", "signal", "geo_type", "geo_value", "time_type", "time_value", "issue")
        q.set_fields(fields_string, fields_int, fields_float)

        # basic query info
        # data type of each field
        # build the source, signal, time, and location (type and id) filters
        q.where_source_signal_pairs("source", "signal", source_signal_pairs)
        q.where_geo_pairs("geo_type", "geo_value", geo_pairs)
        q.where_time_pair("time_type", "time_value", time_pair)

        _handle_lag_issues_as_of(q, issues, lag, as_of)

        try:
            # query = text(f"{str(q)} LIMIT {MAX_RESULTS}")
            query = text(str(q))
            params = q.params
            rows = peekable(parse_row(row, fields_string, fields_int, fields_float) for row in db.execute(query, **params))
        except Exception as e:
            raise DatabaseErrorException(repr(e))

        format = request.values.get("format", "classic")
        try:
            rows.peek()
        except StopIteration:
            if is_compatibility:
                return Response(
                    """{"result": -2, "message": "no results"}""",
                    mimetype="application/json"
                )
            else:
                return Response(
                    """{"epidata": [], "result": -2, "message": "no results"}""",
                    mimetype="application/json"
                )

        try:
            df = generate_transformed_rows3(rows, derived_signals_map, transform_args)
        except Exception as e:
            raise TransformErrorException("Transform exception occurred: " + repr(e))

        if is_compatibility:
            df.drop(columns=["source", "geo_type", "time_type"], inplace=True)

        fields = request.values.get("fields")
        if fields:
            keep_fields = []
            for field in fields.split(","):
                if field.startswith("-") and field[1:] in df.columns:
                    df.drop(columns=[field[1:]], inplace=True)
                elif field in df.columns:
                    keep_fields.append(field)
            if keep_fields:
                df = df[keep_fields]
        else:
            keep_fields = df.columns

        if format == "classic":
            return Response(
                """{"epidata":""" +
                df.to_json(orient="records") +
                """, "result": 1, "message": "success"}""",
                mimetype="application/json"
            )
        elif format == "json":
            return Response(df.to_json(orient="records"), mimetype="application/json")
        elif format == "csv":
            column_order = [
                "geo_value", "signal", "time_value", "direction", "issue", "lag", "missing_value",
                "missing_stderr", "missing_sample_size", "value", "stderr", "sample_size"
            ]
            cols = [col for col in column_order if col in keep_fields]
            filename = "epidata"
            headers = {"Content-Disposition": f"attachment; filename={filename}.csv"} if filename else {}
            return Response(
                df[cols].to_csv(index=False),
                mimetype="text/csv; charset=utf8",
                headers=headers
            )
    else:
        def gen_transform(rows):
            parsed_rows = (parse_row(row, fields_string, fields_int, fields_float) for row in rows)
            for row in parsed_rows:
                yield alias_row(row)

        q.set_order("source", "signal", "geo_type", "geo_value", "time_type", "time_value", "issue")
        q.set_fields(fields_string, fields_int, fields_float)

        # basic query info
        # data type of each field
        # build the source, signal, time, and location (type and id) filters
        q.where_source_signal_pairs("source", "signal", source_signal_pairs)
        q.where_geo_pairs("geo_type", "geo_value", geo_pairs)
        q.where_time_pair("time_type", "time_value", time_pair)

        _handle_lag_issues_as_of(q, issues, lag, as_of)

        p = create_printer()

        # execute first query
        try:
            r = run_query(p, (str(q), q.params))
        except Exception as e:
            raise DatabaseErrorException(str(e))

        # now use a generator for sending the rows and execute all the other queries
        return p(filter_fields(gen_transform(r)))


def _verify_argument_time_type_matches(is_day_argument: bool, count_daily_signal: int, count_weekly_signal: int) -> None:
    if is_day_argument and count_weekly_signal > 0:
        raise ValidationFailedException("day arguments for weekly signals")
    if not is_day_argument and count_daily_signal > 0:
        raise ValidationFailedException("week arguments for daily signals")


@bp.route("/trend", methods=("GET", "POST"))
def handle_trend():
    require_all("window", "date")
    source_signal_pairs = parse_source_signal_pairs()
    daily_signals, weekly_signals = count_signal_time_types(source_signal_pairs)
    source_signal_pairs, alias_mapper = create_source_signal_alias_mapper(source_signal_pairs)
    geo_pairs = parse_geo_pairs()
    transform_args = parse_transform_args()
    jit_bypass = parse_jit_bypass()

    time_window = parse_day_or_week_range_arg("window")
    is_day = time_window.is_day
    time_pair = parse_day_or_week_arg("date")
    time_value, is_also_day = time_pair.time_values[0], time_pair.is_day
    if is_day != is_also_day:
        raise ValidationFailedException("mixing weeks with day arguments")

    _verify_argument_time_type_matches(is_day, daily_signals, weekly_signals)

    basis_time_value = extract_date("basis")
    if basis_time_value is None:
        base_shift = extract_integer("basis_shift")
        if base_shift is None:
            base_shift = 7
        basis_time_value = shift_day_value(time_value, -1 * base_shift) if is_day else shift_week_value(time_value, -1 * base_shift)

    def gen_trend(rows):
        for key, group in groupby(rows, lambda row: (row["source"], row["signal"], row["geo_type"], row["geo_value"])):
            source, signal, geo_type, geo_value = key
            if alias_mapper:
                source = alias_mapper(source, signal)
            trend = compute_trend(geo_type, geo_value, source, signal, time_value, basis_time_value, ((row["time_value"], row["value"]) for row in group))
            yield trend.asdict()

    # build query
    q = QueryBuilder(latest_table, "t")

    fields_string = ["geo_type", "geo_value", "source", "signal"]
    fields_int = ["time_value"]
    fields_float = ["value"]

    use_jit_compute = all((is_day, is_also_day)) and JIT_COMPUTE_ON and not jit_bypass
    if use_jit_compute:
        pad_length = get_pad_length(source_signal_pairs, transform_args.get("smoother_window_length"))
        app.logger.info(f"JIT compute enabled for route '/trend': {source_signal_pairs}")
        source_signal_pairs, derived_signals_map = get_basename_signals_and_derived_map(source_signal_pairs)
        app.logger.info(f"JIT base signals: {source_signal_pairs}")
        time_window = pad_time_window(time_window, pad_length)

        def gen_transform(rows):
            parsed_rows = (parse_row(row, fields_string, fields_int, fields_float) for row in rows)
            transformed_rows = generate_transformed_rows(parsed_rows, derived_signals_map, transform_args)
            for row in transformed_rows:
                yield row
    else:
        def gen_transform(rows):
            parsed_rows = (parse_row(row, fields_string, fields_int, fields_float) for row in rows)
            for row in parsed_rows:
                yield row

    q.set_fields(fields_string, fields_int, fields_float)
    q.set_order("source", "signal", "geo_type", "geo_value", "time_value")

    q.where_source_signal_pairs("source", "signal", source_signal_pairs)
    q.where_geo_pairs("geo_type", "geo_value", geo_pairs)
    q.where_time_pair("time_type", "time_value", time_window)

    # fetch most recent issue fast
    _handle_lag_issues_as_of(q, None, None, None)

    p = create_printer()


    # execute first query
    try:
        r = run_query(p, (str(q), q.params))
    except Exception as e:
        raise DatabaseErrorException(str(e))

    # now use a generator for sending the rows and execute all the other queries
    return p(filter_fields(gen_trend(gen_transform(r))))


@bp.route("/trendseries", methods=("GET", "POST"))
def handle_trendseries():
    require_all("window")
    source_signal_pairs = parse_source_signal_pairs()
    daily_signals, weekly_signals = count_signal_time_types(source_signal_pairs)
    source_signal_pairs, alias_mapper = create_source_signal_alias_mapper(source_signal_pairs)
    geo_pairs = parse_geo_pairs()
    transform_args = parse_transform_args()
    jit_bypass = parse_jit_bypass()

    time_window = parse_day_or_week_range_arg("window")
    is_day = time_window.is_day
    _verify_argument_time_type_matches(is_day, daily_signals, weekly_signals)

    basis_shift = extract_integer(("basis", "basis_shift"))
    if basis_shift is None:
        basis_shift = 7

    shifter = lambda x: shift_day_value(x, -basis_shift)
    if not is_day:
        shifter = lambda x: shift_week_value(x, -basis_shift)

    def gen_trend(rows):
        for key, group in groupby(rows, lambda row: (row["source"], row["signal"], row["geo_type"], row["geo_value"])):
            source, signal, geo_type, geo_value = key
            if alias_mapper:
                source = alias_mapper(source, signal)
            trends = compute_trends(geo_type, geo_value, source, signal, shifter, ((row["time_value"], row["value"]) for row in group))
            for t in trends:
                yield t.asdict()

    # build query
    q = QueryBuilder(latest_table, "t")

    fields_string = ["geo_type", "geo_value", "source", "signal"]
    fields_int = ["time_value"]
    fields_float = ["value"]

    use_jit_compute = is_day and JIT_COMPUTE_ON and not jit_bypass
    if use_jit_compute:
        pad_length = get_pad_length(source_signal_pairs, transform_args.get("smoother_window_length"))
        app.logger.info(f"JIT compute enabled for route '/trendseries': {source_signal_pairs}")
        source_signal_pairs, derived_signals_map = get_basename_signals_and_derived_map(source_signal_pairs)
        app.logger.info(f"JIT base signals: {source_signal_pairs}")
        time_window = pad_time_window(time_window, pad_length)

        def gen_transform(rows):
            parsed_rows = (parse_row(row, fields_string, fields_int, fields_float) for row in rows)
            transformed_rows = generate_transformed_rows(parsed_rows, derived_signals_map, transform_args)
            for row in transformed_rows:
                yield row
    else:
        def gen_transform(rows):
            parsed_rows = (parse_row(row, fields_string, fields_int, fields_float) for row in rows)
            for row in parsed_rows:
                yield row

    q.set_fields(fields_string, fields_int, fields_float)
    q.set_order("source", "signal", "geo_type", "geo_value", "time_value")

    q.where_source_signal_pairs("source", "signal", source_signal_pairs)
    q.where_geo_pairs("geo_type", "geo_value", geo_pairs)
    q.where_time_pair("time_type", "time_value", time_window)

    # fetch most recent issue fast
    _handle_lag_issues_as_of(q, None, None, None)

    p = create_printer()

    # execute first query
    try:
        r = run_query(p, (str(q), q.params))
    except Exception as e:
        raise DatabaseErrorException(str(e))

    # now use a generator for sending the rows and execute all the other queries
    return p(filter_fields(gen_trend(gen_transform(r))))


@bp.route("/correlation", methods=("GET", "POST"))
def handle_correlation():
    require_all("reference", "window", "others", "geo")
    reference = parse_single_source_signal_arg("reference")
    other_pairs = parse_source_signal_arg("others")
    daily_signals, weekly_signals = count_signal_time_types(other_pairs + [reference])
    source_signal_pairs, alias_mapper = create_source_signal_alias_mapper(other_pairs + [reference])
    geo_pairs = parse_geo_arg()
    time_window = parse_day_or_week_range_arg("window")
    is_day = time_window.is_day
    _verify_argument_time_type_matches(is_day, daily_signals, weekly_signals)

    lag = extract_integer("lag")
    if lag is None:
        lag = 28

    # `lag` above is used in post-processing, not in the database query, so we can use latest here
    q = QueryBuilder(latest_table, "t")

    fields_string = ["geo_type", "geo_value", "source", "signal"]
    fields_int = ["time_value"]
    fields_float = ["value"]
    q.set_fields(fields_string, fields_int, fields_float)
    q.set_order("geo_type", "geo_value", "source", "signal", "time_value")

    q.where_source_signal_pairs(
        "source",
        "signal",
        source_signal_pairs,
    )
    q.where_geo_pairs("geo_type", "geo_value", geo_pairs)
    q.where_time_pair("time_type", "time_value", time_window)

    df = as_pandas(str(q), q.params)
    if is_day:
        df["time_value"] = to_datetime(df["time_value"], format="%Y%m%d")
    else:
        # week but convert to date for simpler shifting
        df["time_value"] = to_datetime(df["time_value"].apply(lambda v: time_value_to_week(v).startdate()))

    p = create_printer()

    def prepare_data_frame(df):
        return df[["time_value", "value"]].set_index("time_value")

    def gen():
        by_geo = df.groupby(["geo_type", "geo_value"])
        for (geo_type, geo_value), group in by_geo:
            # group by source, signal
            by_signal = group.groupby(["source", "signal"])

            # find reference group
            # dataframe structure: index=time_value, value=value
            reference_group = next((prepare_data_frame(group) for (source, signal), group in by_signal if source == reference.source and signal == reference.signal[0]), None)

            if reference_group is None or reference_group.empty:
                continue  # no data for reference

            # dataframe structure: index=time_value, value=value
            other_groups = [((source, signal), prepare_data_frame(group)) for (source, signal), group in by_signal if not (source == reference.source and signal == reference.signal[0])]
            if not other_groups:
                continue  # no other signals

            for (source, signal), other_group in other_groups:
                if alias_mapper:
                    source = alias_mapper(source, signal)
                for cor in compute_correlations(geo_type, geo_value, source, signal, lag, reference_group, other_group, is_day):
                    yield cor.asdict()

    # now use a generator for sending the rows and execute all the other queries
    return p(filter_fields(gen()))


@bp.route("/csv", methods=("GET", "POST"))
def handle_export():
    source, signal = request.values.get("signal", "jhu-csse:confirmed_incidence_num").split(":")
    source_signal_pairs = [SourceSignalPair(source, [signal])]
    daily_signals, weekly_signals = count_signal_time_types(source_signal_pairs)
    source_signal_pairs, alias_mapper = create_source_signal_alias_mapper(source_signal_pairs)
    start_pair = parse_day_or_week_arg("start_day", 202001 if weekly_signals > 0 else 20200401)
    start_day, is_day = start_pair.time_values[0], start_pair.is_day
    end_pair = parse_day_or_week_arg("end_day", 202020 if weekly_signals > 0 else 20200901)
    end_day, is_end_day = end_pair.time_values[0], end_pair.is_day
    time_window = TimePair("day" if is_day else "week", [(start_day, end_day)])
    if is_day != is_end_day:
        raise ValidationFailedException("mixing weeks with day arguments")

    _verify_argument_time_type_matches(is_day, daily_signals, weekly_signals)

    transform_args = parse_transform_args()
    jit_bypass = parse_jit_bypass()

    geo_type = request.values.get("geo_type", "county")
    geo_values = request.values.get("geo_values", "*")

    if geo_values != "*":
        geo_values = geo_values.split(",")

    as_of, is_as_of_day = (parse_day_or_week_arg("as_of").time_values[0], parse_day_or_week_arg("as_of").is_day) if "as_of" in request.values else (None, is_day)
    if is_day != is_as_of_day:
        raise ValidationFailedException("mixing weeks with day arguments")

    # build query
    q = QueryBuilder(latest_table, "t")

    fields_string = ["geo_value", "signal", "geo_type", "source"]
    fields_int = ["time_value", "issue", "lag"]
    fields_float = ["value", "stderr", "sample_size"]

    use_jit_compute = all([is_day, is_end_day]) and JIT_COMPUTE_ON and not jit_bypass
    if use_jit_compute:
        pad_length = get_pad_length(source_signal_pairs, transform_args.get("smoother_window_length"))
        app.logger.info(f"JIT compute enabled for route '/csv': {source_signal_pairs}")
        source_signal_pairs, derived_signals_map = get_basename_signals_and_derived_map(source_signal_pairs)
        app.logger.info(f"JIT base signals: {source_signal_pairs}")
        time_window = pad_time_window(time_window, pad_length)

        def gen_transform(rows):
            parsed_rows = (parse_row(row, fields_string, fields_int, fields_float) for row in rows)
            transformed_rows = generate_transformed_rows(parsed_rows, derived_signals_map, transform_args)
            for row in transformed_rows:
                yield row
    else:
        def gen_transform(rows):
            for row in rows:
                yield row

    q.set_fields(fields_string, fields_int, fields_float)
    q.set_order("geo_value", "time_value")
    q.where_source_signal_pairs("source", "signal", source_signal_pairs)
    q.where_time_pair("time_type", "time_value", time_window)
    q.where_geo_pairs("geo_type", "geo_value", [GeoPair(geo_type, True if geo_values == "*" else geo_values)])

    _handle_lag_issues_as_of(q, None, None, as_of)

    format_date = time_value_to_iso if is_day else lambda x: time_value_to_week(x).cdcformat()
    # tag as_of in filename, if it was specified
    as_of_str = "-asof-{as_of}".format(as_of=format_date(as_of)) if as_of is not None else ""
    filename = "covidcast-{source}-{signal}-{start_day}-to-{end_day}{as_of}".format(source=source, signal=signal, start_day=format_date(start_day), end_day=format_date(end_day), as_of=as_of_str)
    p = CSVPrinter(filename)

    def parse_csv_row(i, row):
        # '',geo_value,signal,{time_value,issue},lag,value,stderr,sample_size,geo_type,data_source
        return {
            "": i,
            "geo_value": row["geo_value"],
            "signal": row["signal"],
            "time_value": time_value_to_iso(row["time_value"]) if is_day else row["time_value"],
            "issue": time_value_to_iso(row["issue"]) if is_day and row["issue"] is not None else row["issue"],
            "lag": row["lag"],
            "value": row["value"],
            "stderr": row["stderr"],
            "sample_size": row["sample_size"],
            "geo_type": row["geo_type"],
            "data_source": alias_mapper(row["source"], row["signal"]) if alias_mapper else row["source"],
        }

    def gen_parse(rows):
        for i, row in enumerate(rows):
            yield parse_csv_row(i, row)

    # execute query
    try:
        r = run_query(p, (str(q), q.params))
    except Exception as e:
        raise DatabaseErrorException(str(e))

    # special case for no data to be compatible with the CSV server
    transformed_query = peekable(gen_transform(r))
    first_row = transformed_query.peek(None)
    if not first_row:
        return "No matching data found for signal {source}:{signal} " "at {geo} level from {start_day} to {end_day}, as of {as_of}.".format(
            source=source, signal=signal, geo=geo_type, start_day=format_date(start_day), end_day=format_date(end_day), as_of=(date.today().isoformat() if as_of is None else format_date(as_of))
        )

    # now use a generator for sending the rows and execute all the other queries
    return p(gen_parse(transformed_query))


@bp.route("/backfill", methods=("GET", "POST"))
def handle_backfill():
    """
    example query: http://localhost:5000/covidcast/backfill?signal=fb-survey:smoothed_cli&time=day:20200101-20220101&geo=state:ny&anchor_lag=60
    """
    require_all("geo", "time", "signal")
    signal_pair = parse_single_source_signal_arg("signal")
    daily_signals, weekly_signals = count_signal_time_types([signal_pair])
    source_signal_pairs, _ = create_source_signal_alias_mapper([signal_pair])
    # don't need the alias mapper since we don't return the source

    time_pair = parse_single_time_arg("time")
    is_day = time_pair.is_day
    _verify_argument_time_type_matches(is_day, daily_signals, weekly_signals)

    geo_pair = parse_single_geo_arg("geo")
    reference_anchor_lag = extract_integer("anchor_lag")  # in days or weeks
    if reference_anchor_lag is None:
        reference_anchor_lag = 60

    # build query
    q = QueryBuilder(history_table, "t")

    fields_string = []
    fields_int = ["time_value", "issue"]
    fields_float = ["value", "sample_size"]
    # sort by time value and issue asc
    q.set_order(time_value=True, issue=True)
    q.set_fields(fields_string, fields_int, fields_float, ["is_latest_issue"])

    q.where_source_signal_pairs("source", "signal", source_signal_pairs)
    q.where_geo_pairs("geo_type", "geo_value", [geo_pair])
    q.where_time_pair("time_type", "time_value", time_pair)

    # no restriction of issues or dates since we want all issues
    # _handle_lag_issues_as_of(q, issues, lag, as_of)

    p = create_printer()

    def find_anchor_row(rows: List[Dict[str, Any]], issue: int) -> Optional[Dict[str, Any]]:
        # assume sorted by issue asc
        # find the row that is <= target issue
        i = bisect_right([r["issue"] for r in rows], issue)
        if i:
            return rows[i - 1]
        return None

    def gen(rows):
        # stream per time_value
        for time_value, group in groupby((parse_row(row, fields_string, fields_int, fields_float) for row in rows), lambda row: row["time_value"]):
            # compute data per time value
            issues: List[Dict[str, Any]] = [r for r in group]
            shifted_time_value = shift_day_value(time_value, reference_anchor_lag) if is_day else shift_week_value(time_value, reference_anchor_lag)
            anchor_row = find_anchor_row(issues, shifted_time_value)

            for i, row in enumerate(issues):
                if i > 0:
                    prev_row = issues[i - 1]
                    row["value_rel_change"] = compute_trend_value(row["value"] or 0, prev_row["value"] or 0, 0)
                    if row["sample_size"] is not None:
                        row["sample_size_rel_change"] = compute_trend_value(row["sample_size"] or 0, prev_row["sample_size"] or 0, 0)
                if anchor_row and anchor_row["value"] is not None:
                    row["is_anchor"] = row == anchor_row
                    row["value_completeness"] = (row["value"] or 0) / anchor_row["value"] if anchor_row["value"] else 1
                    if row["sample_size"] is not None:
                        row["sample_size_completeness"] = row["sample_size"] / anchor_row["sample_size"] if anchor_row["sample_size"] else 1
                yield row

    # execute first query
    try:
        r = run_query(p, (q.query, q.params))
    except Exception as e:
        raise DatabaseErrorException(str(e))

    # now use a generator for sending the rows and execute all the other queries
    return p(filter_fields(gen(r)))


@bp.route("/meta", methods=("GET", "POST"))
def handle_meta():
    """
    similar to /covidcast_meta but in a structured optimized JSON form for the app
    """

    filter_signal = parse_source_signal_arg("signal")
    flags = ",".join(request.values.getlist("flags")).split(",")
    filter_smoothed: Optional[bool] = None
    filter_weighted: Optional[bool] = None
    filter_cumulative: Optional[bool] = None
    filter_active: Optional[bool] = None
    filter_time_type: Optional[TimeType] = None

    if "smoothed" in flags:
        filter_smoothed = True
    elif "not_smoothed" in flags:
        filter_smoothed = False
    if "weighted" in flags:
        filter_weighted = True
    elif "not_weighted" in flags:
        filter_weighted = False
    if "cumulative" in flags:
        filter_cumulative = True
    elif "not_cumulative" in flags:
        filter_cumulative = False
    if "active" in flags:
        filter_active = True
    elif "inactive" in flags:
        filter_active = False
    if "day" in flags:
        filter_active = TimeType.day
    elif "week" in flags:
        filter_active = TimeType.week

    row = db.execute(text("SELECT epidata FROM covidcast_meta_cache LIMIT 1")).fetchone()

    data = loads(row["epidata"]) if row and row["epidata"] else []

    by_signal: Dict[Tuple[str, str], List[Dict[str, Any]]] = {}
    for row in data:
        entry = by_signal.setdefault((row["data_source"], row["signal"]), [])
        entry.append(row)

    sources: List[Dict[str, Any]] = []
    for source in data_sources:
        meta_signals: List[Dict[str, Any]] = []

        for signal in source.signals:
            if filter_active is not None and signal.active != filter_active:
                continue
            if filter_signal and all((not s.matches(signal.source, signal.signal) for s in filter_signal)):
                continue
            if filter_smoothed is not None and signal.is_smoothed != filter_smoothed:
                continue
            if filter_weighted is not None and signal.is_weighted != filter_weighted:
                continue
            if filter_cumulative is not None and signal.is_cumulative != filter_cumulative:
                continue
            if filter_time_type is not None and signal.time_type != filter_time_type:
                continue
            meta_data = by_signal.get((source.db_source, signal.signal))
            if not meta_data:
                continue
            row = meta_data[0]
            entry = CovidcastMetaEntry(signal, row["min_time"], row["max_time"], row["max_issue"])
            for row in meta_data:
                entry.intergrate(row)
            meta_signals.append(entry.asdict())

        if not meta_signals:  # none found or no signals
            continue

        s = source.asdict()
        s["signals"] = meta_signals
        sources.append(s)

    return jsonify(sources)


@bp.route("/coverage", methods=("GET", "POST"))
def handle_coverage():
    """
    similar to /signal_dashboard_coverage for a specific signal returns the coverage (number of locations for a given geo_type)
    """

    source_signal_pairs = parse_source_signal_pairs()
    daily_signals, weekly_signals = count_signal_time_types(source_signal_pairs)
    source_signal_pairs, alias_mapper = create_source_signal_alias_mapper(source_signal_pairs)

    geo_type = request.values.get("geo_type", "county")
    if "window" in request.values:
        time_window = parse_day_or_week_range_arg("window")
        is_day = time_window.is_day
    else:
        now_time = extract_date("latest")
        last = extract_integer("days")
        last_weeks = extract_integer("weeks")
        # week if latest is week like or weeks are given otherwise we don't know and guess days
        if (now_time is not None and not guess_time_value_is_day(now_time)) or last_weeks is not None or weekly_signals > 0:
            # week
            if last_weeks is None:
                last_weeks = last or 30
            is_day = False
            now_week = Week.thisweek() if now_time is None else time_value_to_week(now_time)
            time_window = TimePair("week", [(week_to_time_value(now_week - last_weeks), week_to_time_value(now_week))])
        else:
            is_day = True
            if last is None:
                last = 30
            now = date.today() if now_time is None else time_value_to_day(now_time)
            time_window = TimePair("day", [(day_to_time_value(now - timedelta(days=last)), day_to_time_value(now))])
    _verify_argument_time_type_matches(is_day, daily_signals, weekly_signals)

    q = QueryBuilder(latest_table, "c")
    fields_string = ["source", "signal"]
    fields_int = ["time_value"]

    q.set_fields(fields_string, fields_int)

    # manually append the count column because of grouping
    fields_int.append("count")
    q.fields.append(f"count({q.alias}.geo_value) as count")

    if geo_type == "only-county":
        q.where(geo_type="county")
        q.conditions.append('geo_value not like "%000"')
    else:
        q.where(geo_type=geo_type)
    q.where_source_signal_pairs("source", "signal", source_signal_pairs)
    q.where_time_pair("time_type", "time_value", time_window)
    q.group_by = "c.source, c.signal, c.time_value"
    q.set_order("source", "signal", "time_value")

    _handle_lag_issues_as_of(q, None, None, None)

    def transform_row(row, proxy):
        if not alias_mapper or "source" not in row:
            return row
        row["source"] = alias_mapper(row["source"], proxy["signal"])
        return row

    return execute_query(q.query, q.params, fields_string, fields_int, [], transform=transform_row)


@bp.route("/anomalies", methods=("GET", "POST"))
def handle_anomalies():
    """
    proxy to the excel sheet about data anomalies
    """

    df = read_csv(
        "https://docs.google.com/spreadsheets/d/e/2PACX-1vToGcf9x5PNJg-eSrxadoR5b-LM2Cqs9UML97587OGrIX0LiQDcU1HL-L2AA8o5avbU7yod106ih0_n/pub?gid=0&single=true&output=csv", skip_blank_lines=True
    )
    df = df[df["source"].notnull() & df["published"]]
    return print_pandas(df)
