from flask import Blueprint
from werkzeug.exceptions import Unauthorized

from .._common import is_compatibility_mode
from .._params import (
    extract_date,
    extract_dates,
    extract_integer,
    parse_geo_sets,
    parse_source_signal_sets,
    parse_time_set,
)
from .._query import QueryBuilder, execute_query
from .._security import current_user, sources_protected_by_roles
from .covidcast_utils.model import create_source_signal_alias_mapper
from delphi_utils import GeoMapper
from delphi.epidata.common.logger import get_structured_logger

# first argument is the endpoint name
bp = Blueprint("differentiated_access", __name__)
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
                get_structured_logger("covcast_endpt").warning(
                    "non-authZd request for restricted 'source'",
                    api_key=(user and user.api_key),
                    src=src,
                )
        else:
            allowed_source_signal_sets.append(src_sig_set)
    return allowed_source_signal_sets


def serve_geo_restricted(geo_sets: set):
    geomapper = GeoMapper()
    if not current_user:
        raise Unauthorized("User is not authenticated.")
    allowed_counties = set()
    # Getting allowed counties set from user's roles.
    # Example: role 'state:ny' will give user access to all counties in ny state.
    for role in current_user.roles:
        if role.name.startswith("state:"):
            state = role.name.split(":", 1)[1]
            counties_in_state = geomapper.get_geos_within(state, "county", "state")
            allowed_counties.update(counties_in_state)

    for geo_set in geo_sets:
        # Reject if `geo_type` is not county.
        if geo_set.geo_type != "county":
            raise Unauthorized("Only `county` geo_type is allowed")
        # If `geo_value` = '*' then we want to query only that counties that user has access to.
        if geo_set.geo_values is True:
            geo_set.geo_values = list(allowed_counties)
        # Actually we don't need to check whether `geo_set.geo_values` (user requested counties) is a superset of `allowed_counties`
        # We do want to return set of counties that are in both `geo_set.geo_values` and `allowed_counties`
        # Because if user requested less -> we will get only requested list of counties, in other case (user requested more
        # than he can get -> he will get only that counties that he is allowed to).

        # elif set(geo_set.geo_values).issuperset(allowed_counties):
        #     geo_set.geo_values = list(set(geo_set.geo_values).intersection(allowed_counties))

        # If user provided more counties that he is able to query, then we want to show him only
        # that counties that he is allowed to.
        else:
            geo_set.geo_values = list(
                set(geo_set.geo_values).intersection(allowed_counties)
            )
    return geo_sets


@bp.route("/", methods=("GET", "POST"))
def handle():
    source_signal_sets = parse_source_signal_sets()
    source_signal_sets = restrict_by_roles(source_signal_sets)
    source_signal_sets, alias_mapper = create_source_signal_alias_mapper(
        source_signal_sets
    )
    time_set = parse_time_set()
    geo_sets = serve_geo_restricted(parse_geo_sets())

    as_of = extract_date("as_of")
    issues = extract_dates("issues")
    lag = extract_integer("lag")

    # build query
    q = QueryBuilder(latest_table, "t")

    fields_string = ["geo_value", "signal"]
    fields_int = [
        "time_value",
        "direction",
        "issue",
        "lag",
        "missing_value",
        "missing_stderr",
        "missing_sample_size",
    ]
    fields_float = ["value", "stderr", "sample_size"]
    is_compatibility = is_compatibility_mode()
    if is_compatibility:
        q.set_sort_order("signal", "time_value", "geo_value", "issue")
    else:
        # transfer also the new detail columns
        fields_string.extend(["source", "geo_type", "time_type"])
        q.set_sort_order(
            "source",
            "signal",
            "time_type",
            "time_value",
            "geo_type",
            "geo_value",
            "issue",
        )
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
    return execute_query(
        str(q),
        q.params,
        fields_string,
        fields_int,
        fields_float,
        transform=transform_row,
    )
