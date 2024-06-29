from flask import Blueprint, request

from .._exceptions import EpiDataException
from .._params import (
    extract_strings,
    extract_integers,
)
from .._security import current_user
from .._query import filter_strings, execute_query, filter_integers
from .._validate import require_all
from typing import List

# sensor names that require auth tokens to access them;
# excludes the global auth key "sensors" that works for all sensors:
GRANULAR_SENSORS = {
    "twtr",
    "gft",
    "ght",
    "ghtj",
    "cdc",
    "quid",
    "wiki",
}

# A set of sensors that do not require an auth key to access:
OPEN_SENSORS = {
    "sar3",
    "epic",
    "arch",
}

# first argument is the endpoint name
bp = Blueprint("sensors", __name__)
alias = "signals"


def _authenticate(names: List[str]):
    if len(names) == 0:
        raise EpiDataException("no sensor names provided")

    # whether has access to all sensors:
    sensor_authenticated_globally = (current_user and current_user.has_role("sensors"))

    unauthenticated_or_nonexistent_sensors = []
    for name in names:
        if name in OPEN_SENSORS:
            # no auth needed
            continue
        if name in GRANULAR_SENSORS and current_user and current_user.has_role(name):
            # user has permissions for this sensor
            continue
        if not sensor_authenticated_globally:
            # non-existant sensor or auth failed; append to list:
            unauthenticated_or_nonexistent_sensors.append(name)

    if unauthenticated_or_nonexistent_sensors:
        raise EpiDataException(
            f"unauthenticated/nonexistent sensor(s): {','.join(unauthenticated_or_nonexistent_sensors)}"
        )


@bp.route("/", methods=("GET", "POST"))
def handle():
    require_all(request, "names", "locations", "epiweeks")

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
