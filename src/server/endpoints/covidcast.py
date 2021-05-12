from typing import List, Optional, Union, Tuple, Dict, Any
from itertools import groupby
from datetime import date, datetime
from flask import Blueprint, request
from bisect import bisect_right

from .._common import is_compatibility_mode
from .._exceptions import ValidationFailedException, DatabaseErrorException
from .._params import (
    GeoPair,
    SourceSignalPair,
    TimePair,
    parse_geo_arg,
    parse_source_signal_arg,
    parse_time_arg,
    parse_day_arg,
    parse_day_range_arg,
    parse_single_source_signal_arg,
    parse_single_time_arg,
    parse_single_geo_arg,
)
from .._query import QueryBuilder, execute_query, run_query, parse_row
from .._printer import create_printer, CSVPrinter
from .._validate import (
    extract_date,
    extract_dates,
    extract_integer,
    extract_strings,
    require_all,
    require_any,
)
from .._pandas import as_pandas
from .covidcast_utils import compute_trend, shift_time_value, date_to_time_value, time_value_to_iso, compute_correlations, compute_trend_value

# first argument is the endpoint name
bp = Blueprint("covidcast", __name__)
alias = None


def parse_source_signal_pairs() -> List[SourceSignalPair]:
    ds = request.values.get("data_source")
    if ds:
        # old version
        require_any("signal", "signals")
        signals = extract_strings(("signals", "signal"))
        return [SourceSignalPair(ds, signals)]

    if ":" not in request.values.get("signal", ""):
        raise ValidationFailedException("missing parameter: signal or (data_source and signal[s])")

    return parse_source_signal_arg()


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


def parse_time_pairs() -> List[TimePair]:
    time_type = request.values.get("time_type")
    if time_type:
        # old version
        require_all("time_type", "time_values")
        time_values = extract_dates("time_values")
        return [TimePair(time_type, time_values)]

    if ":" not in request.values.get("time", ""):
        raise ValidationFailedException("missing parameter: time or (time_type and time_values)")

    return parse_time_arg()


def _handle_lag_issues_as_of(q: QueryBuilder, issues: Optional[List[Union[Tuple[int, int], int]]] = None, lag: Optional[int] = None, as_of: Optional[int] = None):
    if issues:
        q.where_integers("issue", issues)
    elif lag is not None:
        q.where(lag=lag)
    elif as_of is not None:
        # fetch most recent issues with as of
        sub_condition_asof = "(issue <= :as_of)"
        q.params["as_of"] = as_of
        sub_fields = "max(issue) max_issue, time_type, time_value, `source`, `signal`, geo_type, geo_value"
        sub_group = "time_type, time_value, `source`, `signal`, geo_type, geo_value"
        sub_condition = f"x.max_issue = {q.alias}.issue AND x.time_type = {q.alias}.time_type AND x.time_value = {q.alias}.time_value AND x.source = {q.alias}.source AND x.signal = {q.alias}.signal AND x.geo_type = {q.alias}.geo_type AND x.geo_value = {q.alias}.geo_value"
        q.subquery = f"JOIN (SELECT {sub_fields} FROM {q.table} WHERE {q.conditions_clause} AND {sub_condition_asof} GROUP BY {sub_group}) x ON {sub_condition}"
    else:
        # fetch most recent issue fast
        q.conditions.append(f"({q.alias}.is_latest_issue IS TRUE)")


@bp.route("/", methods=("GET", "POST"))
def handle():
    source_signal_pairs = parse_source_signal_pairs()
    time_pairs = parse_time_pairs()
    geo_pairs = parse_geo_pairs()

    as_of = extract_date("as_of")
    issues = extract_dates("issues")
    lag = extract_integer("lag")

    # build query
    q = QueryBuilder("covidcast", "t")

    fields_string = ["geo_value", "signal"]
    fields_int = ["time_value", "direction", "issue", "lag"]
    fields_float = ["value", "stderr", "sample_size"]
    if is_compatibility_mode():
        q.set_order("signal", "time_value", "geo_value", "issue")
    else:
        # transfer also the new detail columns
        fields_string.extend(["source", "geo_type", "time_type"])
        q.set_order("source", "signal", "time_type", "time_value", "geo_type", "geo_value", "issue")
    q.set_fields(fields_string, fields_int, fields_float)

    # basic query info
    # data type of each field
    # build the source, signal, time, and location (type and id) filters

    q.where_source_signal_pairs("source", "signal", source_signal_pairs)
    q.where_geo_pairs("geo_type", "geo_value", geo_pairs)
    q.where_time_pairs("time_type", "time_value", time_pairs)

    _handle_lag_issues_as_of(q, issues, lag, as_of)

    # send query
    return execute_query(str(q), q.params, fields_string, fields_int, fields_float)


@bp.route("/trend", methods=("GET", "POST"))
def handle_trend():
    require_all("date", "window")
    source_signal_pairs = parse_source_signal_pairs()
    geo_pairs = parse_geo_pairs()

    time_value = parse_day_arg("date")
    time_window = parse_day_range_arg("window")
    basis_time_value = extract_date("basis") or shift_time_value(time_value, -7)

    # build query
    q = QueryBuilder("covidcast", "t")

    fields_string = ["geo_type", "geo_value", "source", "signal"]
    fields_int = ["time_value"]
    fields_float = ["value"]
    q.set_fields(fields_string, fields_int, fields_float)
    q.set_order("geo_type", "geo_value", "source", "signal", "time_value")

    q.where_source_signal_pairs("source", "signal", source_signal_pairs)
    q.where_geo_pairs("geo_type", "geo_value", geo_pairs)
    q.where_time_pairs("time_type", "time_value", [TimePair("day", [time_window])])

    # fetch most recent issue fast
    _handle_lag_issues_as_of(q, None, None, None)

    p = create_printer()

    def gen(rows):
        for key, group in groupby((parse_row(row, fields_string, fields_int, fields_float) for row in rows), lambda row: (row["geo_type"], row["geo_value"], row["source"], row["signal"])):
            trend = compute_trend(key[0], key[1], key[2], key[3], time_value, basis_time_value, ((row["time_value"], row["value"]) for row in group))
            yield trend.asdict()

    # execute first query
    try:
        r = run_query(p, (str(q), q.params))
    except Exception as e:
        raise DatabaseErrorException(str(e))

    # now use a generator for sending the rows and execute all the other queries
    return p(gen(r))


@bp.route("/correlation", methods=("GET", "POST"))
def handle_correlation():
    require_all("reference", "window", "others", "geo")
    reference = parse_single_source_signal_arg("reference")
    other_pairs = parse_source_signal_arg("others")
    geo_pairs = parse_geo_arg()
    time_window = parse_day_range_arg("window")
    lag = extract_integer("lag")
    if lag is None:
        lag = 28

    # build query
    q = QueryBuilder("covidcast", "t")

    fields_string = ["geo_type", "geo_value", "source", "signal"]
    fields_int = ["time_value"]
    fields_float = ["value"]
    q.set_fields(fields_string, fields_int, fields_float)
    q.set_order("geo_type", "geo_value", "source", "signal", "time_value")

    q.where_source_signal_pairs("source", "signal", other_pairs + [reference])
    q.where_geo_pairs("geo_type", "geo_value", geo_pairs)
    q.where_time_pairs("time_type", "time_value", [TimePair("day", [time_window])])

    # fetch most recent issue fast
    q.conditions.append(f"({q.alias}.is_latest_issue IS TRUE)")

    df = as_pandas(str(q), q.params, parse_dates={"time_value": "%Y%m%d"})

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
                for cor in compute_correlations(geo_type, geo_value, source, signal, lag, reference_group, other_group):
                    yield cor.asdict()

    # now use a generator for sending the rows and execute all the other queries
    return p(gen())


@bp.route("/csv", methods=("GET", "POST"))
def handle_export():
    source, signal = request.args.get("signal", "jhu-csse:confirmed_incidence_num").split(":")
    start_day = request.args.get("start_day", "2020-04-01")
    end_day = request.args.get("end_day", "2020-09-01")
    geo_type = request.args.get("geo_type", "county")
    geo_values = request.args.get("geo_values", "*")

    if geo_values != "*":
        geo_values = geo_values.split(",")

    as_of = request.args.get("as_of", None)

    start_day = datetime.strptime(start_day, "%Y-%m-%d").date()
    end_day = datetime.strptime(end_day, "%Y-%m-%d").date()

    if as_of is not None:
        as_of = datetime.strptime(as_of, "%Y-%m-%d").date()

    # build query
    q = QueryBuilder("covidcast", "t")

    q.set_fields(["geo_value", "signal", "time_value", "issue", "lag", "value", "stderr", "sample_size", "geo_type", "source"], [], [])
    q.set_order("geo_value", "time_value")
    q.where(source=source, signal=signal, time_type="day")
    q.conditions.append("time_value BETWEEN :start_day AND :end_day")
    q.params["start_day"] = date_to_time_value(start_day)
    q.params["end_day"] = date_to_time_value(end_day)
    q.where_geo_pairs("geo_type", "geo_value", [GeoPair(geo_type, True if geo_values == "*" else geo_values)])

    _handle_lag_issues_as_of(q, None, None, date_to_time_value(as_of) if as_of is not None else None)

    # tag as_of in filename, if it was specified
    as_of_str = "-asof-{as_of}".format(as_of=as_of.isoformat()) if as_of is not None else ""
    filename = "covidcast-{source}-{signal}-{start_day}-to-{end_day}{as_of}".format(source=source, signal=signal, start_day=start_day.isoformat(), end_day=end_day.isoformat(), as_of=as_of_str)
    p = CSVPrinter(filename)

    def parse_row(i, row):
        # '',geo_value,signal,{time_value,issue},lag,value,stderr,sample_size,geo_type,data_source
        return {
            "": i,
            "geo_value": row["geo_value"],
            "signal": row["signal"],
            "time_value": time_value_to_iso(row["time_value"]),
            "issue": time_value_to_iso(row["issue"]),
            "lag": row["lag"],
            "value": row["value"],
            "stderr": row["stderr"],
            "sample_size": row["sample_size"],
            "geo_type": row["geo_type"],
            "data_source": row["source"],
        }

    def gen(first_row, rows):
        yield parse_row(0, first_row)
        for i, row in enumerate(rows):
            yield parse_row(i + 1, row)

    # execute query
    try:
        r = run_query(p, (str(q), q.params))
    except Exception as e:
        raise DatabaseErrorException(str(e))

    # special case for no data to be compatible with the CSV server
    first_row = next(r, None)
    if not first_row:
        return "No matching data found for signal {source}:{signal} " "at {geo} level from {start_day} to {end_day}, as of {as_of}.".format(
            source=source, signal=signal, geo=geo_type, start_day=start_day.isoformat(), end_day=end_day.isoformat(), as_of=(date.today().isoformat() if as_of is None else as_of.isoformat())
        )

    # now use a generator for sending the rows and execute all the other queries
    return p(gen(first_row, r))


@bp.route("/backfill", methods=("GET", "POST"))
def handle_backfill():
    """
    example query: http://localhost:5000/covidcast/backfill?signal=fb-survey:smoothed_cli&time=day:20200101-20220101&geo=state:ny&anchor_lag=60
    """
    require_all("geo", "time", "signal")
    signal_pair = parse_single_source_signal_arg("signal")
    time_pair = parse_single_time_arg("time")
    geo_pair = parse_single_geo_arg("geo")
    reference_anchor_lag = extract_integer("anchor_lag")  # in days
    if reference_anchor_lag is None:
        reference_anchor_lag = 60

    # build query
    q = QueryBuilder("covidcast", "t")

    fields_string = []
    fields_int = ["time_value", "issue"]
    fields_float = ["value", "sample_size"]
    # sort by time value and issue asc
    q.set_order(time_value=True, issue=True)
    q.set_fields(fields_string, fields_int, fields_float, ["is_latest_issue"])

    q.where_source_signal_pairs("source", "signal", [signal_pair])
    q.where_geo_pairs("geo_type", "geo_value", [geo_pair])
    q.where_time_pairs("time_type", "time_value", [time_pair])

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
            anchor_row = find_anchor_row(issues, shift_time_value(time_value, reference_anchor_lag))

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
    return p(gen(r))
