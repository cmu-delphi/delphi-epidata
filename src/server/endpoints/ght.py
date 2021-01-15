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
    q.fields = "g.epiweek, g.location, g.value"
    q.order = "g.epiweek ASC, g.location ASC"

    # build the filter
    q.where_strings("location", locations)
    q.where_integers("epiweek", epiweeks)
    q.where(query=query)

    fields_string = ["location"]
    fields_int = ["epiweek"]
    fields_float = ["value"]

    # send query
    return execute_query(str(q), q.params, fields_string, fields_int, fields_float)
