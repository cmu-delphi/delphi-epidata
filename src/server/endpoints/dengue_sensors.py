from flask import Blueprint

from .._config import AUTH
from .._query import execute_query, filter_integers, filter_strings
from .._validate import check_auth_token, extract_integers, extract_strings, require_all

# first argument is the endpoint name
bp = Blueprint("dengue_sensors", __name__)
alias = None


@bp.route("/", methods=("GET", "POST"))
def handle():
    check_auth_token(AUTH["sensors"])
    require_all("names", "locations", "epiweeks")

    names = extract_strings("names")
    locations = extract_strings("locations")
    epiweeks = extract_integers("epiweeks")

    # build query
    table = "`dengue_sensors` s"
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
