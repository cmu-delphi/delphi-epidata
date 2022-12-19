from flask import Blueprint, request

from .._config import AUTH
from .._query import execute_query, QueryBuilder
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
    q = QueryBuilder("ght", "g")

    fields_string = ["location"]
    fields_int = ["epiweek"]
    fields_float = ["value"]
    q.set_select_fields(fields_string, fields_int, fields_float)

    q.set_sort_order("epiweek", "location")

    # build the filter
    q.apply_string_filters("location", locations)
    q.apply_integer_filters("epiweek", epiweeks)
    q.apply_filter(query=query)

    # send query
    return execute_query(str(q), q.params, fields_string, fields_int, fields_float)
