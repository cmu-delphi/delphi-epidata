from flask import Blueprint

from .._validate import (
    require_all,
    extract_strings,
    extract_integers,
)
from .._security import current_user
from .._config import GRANULAR_SENSOR_ROLES, OPEN_SENSORS, UserRole
from .._query import filter_strings, execute_query, filter_integers
from .._exceptions import EpiDataException
from typing import List

# first argument is the endpoint name
bp = Blueprint("sensors", __name__)
alias = "signals"


def _authenticate(names: List[str]):
    names = extract_strings("names")
    n_names = len(names)

    # The number of valid granular tokens is related to the number of auth token checks that a single query could perform.  Use the max number of valid granular auth tokens per name in the check below as a way to prevent leakage of sensor names (but revealing the number of sensor names) via this interface.  Treat all sensors as non-open for convenience of calculation.
    if n_names == 0:
        # Check whether no names were provided to prevent edge-case issues in error message below, and in case surrounding behavior changes in the future:
        raise EpiDataException("no sensor names provided")

    unauthenticated_or_nonexistent_sensors = []
    for name in names:
        sensor_is_open = name in OPEN_SENSORS
        # test whether they provided the "global" auth token that works for all sensors:
        sensor_authenticated_globally = current_user.has_role(UserRole.sensors)
        # test whether they provided a "granular" auth token for one of the
        # sensor_subsets containing this sensor (if any):
        sensor_authenticated_granularly = False
        if name in GRANULAR_SENSOR_ROLES and current_user.has_role(GRANULAR_SENSOR_ROLES[name]):
            sensor_authenticated_granularly = True
        # (else: there are no granular tokens for this sensor; can't authenticate granularly)

        if not sensor_is_open and not sensor_authenticated_globally and not sensor_authenticated_granularly:
            # authentication failed for this sensor; append to list:
            unauthenticated_or_nonexistent_sensors.append(name)

    if unauthenticated_or_nonexistent_sensors:
        raise EpiDataException(
            f"unauthenticated/nonexistent sensor(s): {','.join(unauthenticated_or_nonexistent_sensors)}"
        )
        # # Alternative message that may enable shorter tokens:
        # $data['message'] = 'some/all sensors requested were unauthenticated/nonexistent';


@bp.route("/", methods=("GET", "POST"))
def handle():
    require_all("names", "locations", "epiweeks")

    names = extract_strings("names") or []
    _authenticate(names)

    # parse the request
    locations = extract_strings("locations")
    epiweeks = extract_integers("epiweeks")

    # build query
    table = "`sensors` s"
    fields = "s.`name`, s.`location`, s.`epiweek`, s.`value`"
    # basic query info
    order = "s.`epiweek` ASC, s.`name` ASC, s.`location` ASC"
    # build the filter
    params = dict()
    condition_name = filter_strings("s.`name`", names, "name", params)
    # build the location filter
    condition_location = filter_strings("s.`location`", locations, "loc", params)
    # build the epiweek filter
    condition_epiweek = filter_integers("s.`epiweek`", epiweeks, "epiweek", params)
    # the query
    query = f"SELECT {fields} FROM {table} WHERE ({condition_name}) AND ({condition_location}) AND ({condition_epiweek}) ORDER BY {order}"

    fields_string = ["name", "location"]
    fields_int = ["epiweek"]
    fields_float = ["value"]

    # send query
    return execute_query(query, params, fields_string, fields_int, fields_float)
