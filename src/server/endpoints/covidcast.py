from typing import List, Optional, Tuple, Dict, Any
from itertools import groupby
from datetime import date, timedelta
from epiweeks import Week
from flask import Blueprint, request
from flask.json import loads, jsonify
from bisect import bisect_right
from sqlalchemy import text
from pandas import read_csv, to_datetime

from .._common import is_compatibility_mode, db
from .._exceptions import ValidationFailedException, DatabaseErrorException
from .._params import (
    GeoSet,
    SourceSignalSet,
    TimeSet,
    extract_date,
    extract_dates,
    extract_integer,
    parse_geo_arg,
    parse_source_signal_arg,
    parse_day_or_week_arg,
    parse_day_or_week_range_arg,
    parse_single_source_signal_arg,
    parse_single_time_arg,
    parse_single_geo_arg,
    parse_geo_sets,
    parse_source_signal_sets,
    parse_time_set,
)
from .._query import QueryBuilder, execute_query, run_query, parse_row, filter_fields
from .._printer import create_printer, CSVPrinter
from .._security import current_user, sources_protected_by_roles
from .._validate import require_all
from .._pandas import as_pandas, print_pandas
from .covidcast_utils import compute_trend, compute_trends, compute_trend_value, CovidcastMetaEntry
from ..utils import shift_day_value, day_to_time_value, time_value_to_iso, time_value_to_day, shift_week_value, time_value_to_week, guess_time_value_is_day, week_to_time_value, TimeValues
from .covidcast_utils.model import TimeType, count_signal_time_types, data_sources, create_source_signal_alias_mapper
from delphi_utils import get_structured_logger

# first argument is the endpoint name
bp = Blueprint("covidcast", __name__)
alias = None

latest_table = "epimetric_latest_v"
history_table = "epimetric_full_v"

def restrict_by_roles(source_signal_sets):
    # takes a list of SourceSignalSet objects
    # and returns only those from the list
    # that the current user is permitted to access.
    user = current_user
    allowed_source_signal_sets = []
    for src_sig_set in source_signal_sets:
        src = src_sig_set.source
        if src in sources_protected_by_roles:
            role = sources_protected_by_roles[src]
            if user and user.has_role(role):
                allowed_source_signal_sets.append(src_sig_set)
            else:
                # protected src and user does not have permission => leave it out of the srcsig sets
                get_structured_logger("covcast_endpt").warning("non-authZd request for restricted 'source'", api_key=(user and user.api_key), src=src)
        else:
            allowed_source_signal_sets.append(src_sig_set)
    return allowed_source_signal_sets


@bp.route("/", methods=("GET", "POST"))
def handle():
    source_signal_sets = parse_source_signal_sets()
    source_signal_sets = restrict_by_roles(source_signal_sets)
    source_signal_sets, alias_mapper = create_source_signal_alias_mapper(source_signal_sets)
    time_set = parse_time_set()
    geo_sets = parse_geo_sets()

    as_of = extract_date("as_of")
    issues = extract_dates("issues")
    lag = extract_integer("lag")

    # build query
    q = QueryBuilder(latest_table, "t")

    fields_string = ["geo_value", "signal"]
    fields_int = ["time_value", "direction", "issue", "lag", "missing_value", "missing_stderr", "missing_sample_size"]
    fields_float = ["value", "stderr", "sample_size"]
    is_compatibility = is_compatibility_mode()
    if is_compatibility:
        q.set_sort_order("signal", "time_value", "geo_value", "issue")
    else:
        # transfer also the new detail columns
        fields_string.extend(["source", "geo_type", "time_type"])
        q.set_sort_order("source", "signal", "time_type", "time_value", "geo_type", "geo_value", "issue")
    q.set_fields(fields_string, fields_int, fields_float)

    # basic query info
    # data type of each field
    # build the source, signal, time, and location (type and id) filters

    q.apply_source_signal_filters("source", "signal", source_signal_sets)
    q.apply_geo_filters("geo_type", "geo_value", geo_sets)
    q.apply_time_filter("time_type", "time_value", time_set)

    q.apply_issues_filter(history_table, issues)
    q.apply_lag_filter(history_table, lag)
    q.apply_as_of_filter(history_table, as_of)

    def transform_row(row, proxy):
        if is_compatibility or not alias_mapper or "source" not in row:
            return row
        row["source"] = alias_mapper(row["source"], proxy["signal"])
        return row

    # send query
    return execute_query(str(q), q.params, fields_string, fields_int, fields_float, transform=transform_row)


def _verify_argument_time_type_matches(is_day_argument: bool, count_daily_signal: int, count_weekly_signal: int) -> None:
    if is_day_argument and count_weekly_signal > 0:
        raise ValidationFailedException("day arguments for weekly signals")
    if not is_day_argument and count_daily_signal > 0:
        raise ValidationFailedException("week arguments for daily signals")


@bp.route("/trend", methods=("GET", "POST"))
def handle_trend():
    require_all(request, "window", "date")
    source_signal_sets = parse_source_signal_sets()
    source_signal_sets = restrict_by_roles(source_signal_sets)
    daily_signals, weekly_signals = count_signal_time_types(source_signal_sets)
    source_signal_sets, alias_mapper = create_source_signal_alias_mapper(source_signal_sets)
    geo_sets = parse_geo_sets()

    time_window = parse_day_or_week_range_arg("window")
    is_day = time_window.is_day
    time_set = parse_day_or_week_arg("date")
    time_value, is_also_day = time_set.time_values[0], time_set.is_day
    if is_day != is_also_day:
        raise ValidationFailedException("mixing weeks with day arguments")
    _verify_argument_time_type_matches(is_day, daily_signals, weekly_signals)
    basis_time_value = extract_date("basis")
    if basis_time_value is None:
        base_shift = extract_integer("basis_shift")
        if base_shift is None:
            base_shift = 7
        basis_time_value = shift_day_value(time_value, -1 * base_shift) if is_day else shift_week_value(time_value, -1 * base_shift)

    # build query
    q = QueryBuilder(latest_table, "t")

    fields_string = ["geo_type", "geo_value", "source", "signal"]
    fields_int = ["time_value"]
    fields_float = ["value"]
    q.set_fields(fields_string, fields_int, fields_float)
    q.set_sort_order("geo_type", "geo_value", "source", "signal", "time_value")

    q.apply_source_signal_filters("source", "signal", source_signal_sets)
    q.apply_geo_filters("geo_type", "geo_value", geo_sets)
    q.apply_time_filter("time_type", "time_value", time_window)

    p = create_printer(request.values.get("format"))

    def gen(rows):
        for key, group in groupby((parse_row(row, fields_string, fields_int, fields_float) for row in rows), lambda row: (row["geo_type"], row["geo_value"], row["source"], row["signal"])):
            geo_type, geo_value, source, signal = key
            if alias_mapper:
                source = alias_mapper(source, signal)
            trend = compute_trend(geo_type, geo_value, source, signal, time_value, basis_time_value, ((row["time_value"], row["value"]) for row in group))
            yield trend.asdict()

    # execute first query
    try:
        r = run_query(p, (str(q), q.params))
    except Exception as e:
        raise DatabaseErrorException(str(e))

    # now use a generator for sending the rows and execute all the other queries
    return p(filter_fields(gen(r)))


@bp.route("/trendseries", methods=("GET", "POST"))
def handle_trendseries():
    require_all(request, "window")
    source_signal_sets = parse_source_signal_sets()
    source_signal_sets = restrict_by_roles(source_signal_sets)
    daily_signals, weekly_signals = count_signal_time_types(source_signal_sets)
    source_signal_sets, alias_mapper = create_source_signal_alias_mapper(source_signal_sets)
    geo_sets = parse_geo_sets()

    time_window = parse_day_or_week_range_arg("window")
    is_day = time_window.is_day
    _verify_argument_time_type_matches(is_day, daily_signals, weekly_signals)
    basis_shift = extract_integer(("basis", "basis_shift"))
    if basis_shift is None:
        basis_shift = 7

    # build query
    q = QueryBuilder(latest_table, "t")

    fields_string = ["geo_type", "geo_value", "source", "signal"]
    fields_int = ["time_value"]
    fields_float = ["value"]
    q.set_fields(fields_string, fields_int, fields_float)
    q.set_sort_order("geo_type", "geo_value", "source", "signal", "time_value")

    q.apply_source_signal_filters("source", "signal", source_signal_sets)
    q.apply_geo_filters("geo_type", "geo_value", geo_sets)
    q.apply_time_filter("time_type", "time_value", time_window)

    p = create_printer(request.values.get("format"))

    shifter = lambda x: shift_day_value(x, -basis_shift)
    if not is_day:
        shifter = lambda x: shift_week_value(x, -basis_shift)

    def gen(rows):
        for key, group in groupby((parse_row(row, fields_string, fields_int, fields_float) for row in rows), lambda row: (row["geo_type"], row["geo_value"], row["source"], row["signal"])):
            geo_type, geo_value, source, signal = key
            if alias_mapper:
                source = alias_mapper(source, signal)
            trends = compute_trends(geo_type, geo_value, source, signal, shifter, ((row["time_value"], row["value"]) for row in group))
            for t in trends:
                yield t.asdict()

    # execute first query
    try:
        r = run_query(p, (str(q), q.params))
    except Exception as e:
        raise DatabaseErrorException(str(e))

    # now use a generator for sending the rows and execute all the other queries
    return p(filter_fields(gen(r)))


@bp.route("/csv", methods=("GET", "POST"))
def handle_export():
    source, signal = request.values.get("signal", "jhu-csse:confirmed_incidence_num").split(":")
    source_signal_sets = [SourceSignalSet(source, [signal])]
    source_signal_sets = restrict_by_roles(source_signal_sets)
    daily_signals, weekly_signals = count_signal_time_types(source_signal_sets)
    source_signal_sets, alias_mapper = create_source_signal_alias_mapper(source_signal_sets)
    start_time_set = parse_day_or_week_arg("start_day", 202001 if weekly_signals > 0 else 20200401)
    start_day, is_day = start_time_set.time_values[0], start_time_set.is_day
    end_time_set = parse_day_or_week_arg("end_day", 202020 if weekly_signals > 0 else 20200901)
    end_day, is_end_day = end_time_set.time_values[0], end_time_set.is_day
    if is_day != is_end_day:
        raise ValidationFailedException("mixing weeks with day arguments")
    _verify_argument_time_type_matches(is_day, daily_signals, weekly_signals)

    geo_type = request.values.get("geo_type", "county")
    geo_values = request.values.get("geo_values", "*")

    if geo_values != "*":
        geo_values = geo_values.split(",")

    as_of, is_as_of_day = (parse_day_or_week_arg("as_of").time_values[0], parse_day_or_week_arg("as_of").is_day) if "as_of" in request.values else (None, is_day)
    if is_day != is_as_of_day:
        raise ValidationFailedException("mixing weeks with day arguments")

    # build query
    q = QueryBuilder(latest_table, "t")

    q.set_fields(["geo_value", "signal", "time_value", "issue", "lag", "value", "stderr", "sample_size", "geo_type", "source"], [], [])

    q.set_sort_order("time_value", "geo_value")
    q.apply_source_signal_filters("source", "signal", source_signal_sets)
    q.apply_time_filter("time_type", "time_value", TimeSet("day" if is_day else "week", [(start_day, end_day)]))
    q.apply_geo_filters("geo_type", "geo_value", [GeoSet(geo_type, True if geo_values == "*" else geo_values)])

    q.apply_as_of_filter(history_table, as_of)

    format_date = time_value_to_iso if is_day else lambda x: time_value_to_week(x).cdcformat()
    # tag as_of in filename, if it was specified
    as_of_str = "-asof-{as_of}".format(as_of=format_date(as_of)) if as_of is not None else ""
    filename = "covidcast-{source}-{signal}-{start_day}-to-{end_day}{as_of}".format(source=source, signal=signal, start_day=format_date(start_day), end_day=format_date(end_day), as_of=as_of_str)
    p = CSVPrinter(filename)

    def parse_row(i, row):
        # '',geo_value,signal,{time_value,issue},lag,value,stderr,sample_size,geo_type,data_source
        return {
            "": i,
            "geo_value": row["geo_value"],
            "signal": row["signal"],
            "time_value": time_value_to_iso(row["time_value"]) if is_day else row["time_value"],
            "issue": time_value_to_iso(row["issue"]) if is_day else row["issue"],
            "lag": row["lag"],
            "value": row["value"],
            "stderr": row["stderr"],
            "sample_size": row["sample_size"],
            "geo_type": row["geo_type"],
            "data_source": alias_mapper(row["source"], row["signal"]) if alias_mapper else row["source"],
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
            source=source, signal=signal, geo=geo_type, start_day=format_date(start_day), end_day=format_date(end_day), as_of=(date.today().isoformat() if as_of is None else format_date(as_of))
        )

    # now use a generator for sending the rows and execute all the other queries
    return p(gen(first_row, r))


@bp.route("/backfill", methods=("GET", "POST"))
def handle_backfill():
    """
    example query: http://localhost:5000/covidcast/backfill?signal=fb-survey:smoothed_cli&time=day:20200101-20220101&geo=state:ny&anchor_lag=60
    """
    require_all(request, "geo", "time", "signal")
    source_signal_sets = [parse_single_source_signal_arg("signal")]
    source_signal_sets = restrict_by_roles(source_signal_sets)
    daily_signals, weekly_signals = count_signal_time_types(source_signal_sets)
    source_signal_sets, _ = create_source_signal_alias_mapper(source_signal_sets)
    # don't need the alias mapper since we don't return the source

    time_set = parse_single_time_arg("time")
    is_day = time_set.is_day
    _verify_argument_time_type_matches(is_day, daily_signals, weekly_signals)

    geo_set = parse_single_geo_arg("geo")
    reference_anchor_lag = extract_integer("anchor_lag")  # in days or weeks
    if reference_anchor_lag is None:
        reference_anchor_lag = 60

    # build query
    q = QueryBuilder(history_table, "t")

    fields_string = []
    fields_int = ["time_value", "issue"]
    fields_float = ["value", "sample_size"]
    # sort by time value and issue asc
    q.set_sort_order("time_value", "issue")
    q.set_fields(fields_string, fields_int, fields_float, ["is_latest_issue"])

    q.apply_source_signal_filters("source", "signal", source_signal_sets)
    q.apply_geo_filters("geo_type", "geo_value", [geo_set])
    q.apply_time_filter("time_type", "time_value", time_set)

    p = create_printer(request.values.get("format"))

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

    user = current_user
    sources: List[Dict[str, Any]] = []
    for source in data_sources:
        src = source.db_source
        if src in sources_protected_by_roles:
            role = sources_protected_by_roles[src]
            if not (user and user.has_role(role)):
                # if this is a protected source
                # and the user doesnt have the allowed role
                # (or if we have no user)
                # then skip this source
                continue

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

    source_signal_sets = parse_source_signal_sets()
    source_signal_sets = restrict_by_roles(source_signal_sets)
    daily_signals, weekly_signals = count_signal_time_types(source_signal_sets)
    source_signal_sets, alias_mapper = create_source_signal_alias_mapper(source_signal_sets)

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
            time_window = TimeSet("week", [(week_to_time_value(now_week - last_weeks), week_to_time_value(now_week))])
        else:
            is_day = True
            if last is None:
                last = 30
            now = date.today() if now_time is None else time_value_to_day(now_time)
            time_window = TimeSet("day", [(day_to_time_value(now - timedelta(days=last)), day_to_time_value(now))])
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
    q.apply_source_signal_filters("source", "signal", source_signal_sets)
    q.apply_time_filter("time_type", "time_value", time_window)
    q.group_by = "c.source, c.signal, c.time_value"
    q.set_sort_order("source", "signal", "time_value")

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
