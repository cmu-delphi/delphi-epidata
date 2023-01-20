from flask import Blueprint, Request, request

from .._config import AUTH, GRANULAR_SENSOR_AUTH_TOKENS, OPEN_SENSORS
from .._exceptions import EpiDataException
from .._params import (
    extract_strings,
    extract_integers,
)
from .._query import filter_strings, execute_query, filter_integers
from .._validate import (
    require_all,
    resolve_auth_token,
)
from typing import List

# first argument is the endpoint name
bp = Blueprint("sensors", __name__)
alias = "signals"

#   Limits on the number of effective auth token equality checks performed per sensor query; generate auth tokens with appropriate levels of entropy according to the limits below:
MAX_GLOBAL_AUTH_CHECKS_PER_SENSOR_QUERY = 1  # (but imagine is larger to futureproof)
MAX_GRANULAR_AUTH_CHECKS_PER_SENSOR_QUERY = 30  # (but imagine is larger to futureproof)
#   A (currently redundant) limit on the number of auth tokens that can be provided:
MAX_AUTH_KEYS_PROVIDED_PER_SENSOR_QUERY = 1
# end sensor query authentication configuration

PHP_INT_MAX = 2147483647


def _authenticate(req: Request, names: List[str]):
    auth_tokens_presented = (resolve_auth_token(req) or "").split(",")

    names = extract_strings("names")
    n_names = len(names)
    n_auth_tokens_presented = len(auth_tokens_presented)

    max_valid_granular_tokens_per_name = max(
        len(v) for v in GRANULAR_SENSOR_AUTH_TOKENS.values()
    )

    # The number of valid granular tokens is related to the number of auth token checks that a single query could perform.  Use the max number of valid granular auth tokens per name in the check below as a way to prevent leakage of sensor names (but revealing the number of sensor names) via this interface.  Treat all sensors as non-open for convenience of calculation.
    if n_names == 0:
        # Check whether no names were provided to prevent edge-case issues in error message below, and in case surrounding behavior changes in the future:
        raise EpiDataException("no sensor names provided")
    if n_auth_tokens_presented > 1:
        raise EpiDataException(
            "currently, only a single auth token is allowed to be presented at a time; please issue a separate query for each sensor name using only the corresponding token"
        )

    # Check whether max number of presented-vs.-acceptable token comparisons that would be performed is over the set limits, avoiding calculation of numbers > PHP_INT_MAX/100:
    #   Global auth token comparison limit check:
    #   Granular auth token comparison limit check:
    if (
        n_auth_tokens_presented > MAX_GLOBAL_AUTH_CHECKS_PER_SENSOR_QUERY
        or n_names
        > int((PHP_INT_MAX / 100 - 1) / max(1, max_valid_granular_tokens_per_name))
        or n_auth_tokens_presented
        > int(PHP_INT_MAX / 100 / max(1, n_names * max_valid_granular_tokens_per_name))
        or n_auth_tokens_presented * n_names * max_valid_granular_tokens_per_name
        > MAX_GRANULAR_AUTH_CHECKS_PER_SENSOR_QUERY
    ):
        raise EpiDataException(
            "too many sensors requested and/or auth tokens presented; please divide sensors into batches and/or use only the tokens needed for the sensors requested"
        )

    if len(auth_tokens_presented) > MAX_AUTH_KEYS_PROVIDED_PER_SENSOR_QUERY:
        # this check should be redundant with >1 check as well as global check above
        raise EpiDataException("too many auth tokens presented")

    unauthenticated_or_nonexistent_sensors = []
    for name in names:
        sensor_is_open = name in OPEN_SENSORS
        # test whether they provided the "global" auth token that works for all sensors:
        sensor_authenticated_globally = AUTH["sensors"] in auth_tokens_presented
        # test whether they provided a "granular" auth token for one of the
        # sensor_subsets containing this sensor (if any):
        sensor_authenticated_granularly = False
        if name in GRANULAR_SENSOR_AUTH_TOKENS:
            acceptable_granular_tokens_for_sensor = GRANULAR_SENSOR_AUTH_TOKENS[name]
            # check for nonempty intersection between provided and acceptable
            # granular auth tokens:
            for acceptable_granular_token in acceptable_granular_tokens_for_sensor:
                if acceptable_granular_token in auth_tokens_presented:
                    sensor_authenticated_granularly = True
                    break
        # (else: there are no granular tokens for this sensor; can't authenticate granularly)

        if (
            not sensor_is_open
            and not sensor_authenticated_globally
            and not sensor_authenticated_granularly
        ):
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
    require_all(request, "names", "locations", "epiweeks")

    names = extract_strings("names") or []
    _authenticate(request, names)

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
