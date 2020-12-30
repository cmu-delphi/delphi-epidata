from flask import Blueprint, request

from .._config import AUTH
from .._query import execute_query, filter_integers, filter_strings
from .._validate import check_auth_token, extract_integers, extract_strings, require_all

# first argument is the endpoint name
bp = Blueprint("ght", __name__)
alias = None


@bp.route("/", methods=("GET", "POST"))
def handle():
    check_auth_token(AUTH["ght"])
    require_all("locations", "epiweeks", "query")

    locations = extract_strings("locations")
    epiweeks = extract_integers("epiweeks")
    query = request.values["query"]

    # build query
    table = "`gth` g"
    fields = "g.`epiweek`, g.`location`, g.`value`"
    order = "g.`epiweek` ASC, g.`location` ASC"

    # build the filter
    params = dict()
    condition_epiweek = filter_integers("g.`epiweek`", epiweeks, "epiweek", params)
    # build the location filter
    condition_location = filter_strings("g.`location`", locations, "loc", params)
    condition_query = filter_strings("g.`query`", [query], "query", params)
    # the query
    query = f"SELECT {fields} FROM {table} WHERE ({condition_epiweek}) AND ({condition_location}) AND ({condition_query}) ORDER BY {order}"

    fields_string = ["location"]
    fields_int = ["epiweek"]
    fields_float = ["value"]

    # send query
    return execute_query(query, params, fields_string, fields_int, fields_float)
