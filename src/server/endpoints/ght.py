from flask import Blueprint, request

from .._query import execute_query, QueryBuilder
from .._validate import extract_integers, extract_strings, require_all
from .._security import require_role

# first argument is the endpoint name
bp = Blueprint("ght", __name__)
alias = None


@bp.route("/", methods=("GET", "POST"))
@require_role("ght")
def handle():
    require_all("locations", "epiweeks", "query")

    locations = extract_strings("locations")
    epiweeks = extract_integers("epiweeks")
    query = request.values["query"]

    # build query
    q = QueryBuilder("ght", "g")

    fields_string = ["location"]
    fields_int = ["epiweek"]
    fields_float = ["value"]
    q.set_fields(fields_string, fields_int, fields_float)

    q.set_order("epiweek", "location")

    # build the filter
    q.where_strings("location", locations)
    q.where_integers("epiweek", epiweeks)
    q.where(query=query)

    # send query
    return execute_query(str(q), q.params, fields_string, fields_int, fields_float)
