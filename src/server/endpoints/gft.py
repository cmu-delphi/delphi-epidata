from flask import Blueprint

from .._query import execute_query, QueryBuilder
from .._validate import extract_integers, extract_strings, require_all

# first argument is the endpoint name
bp = Blueprint("gft", __name__)
required_role = None
alias = None


@bp.route("/", methods=("GET", "POST"))
def handle():
    require_all("locations", "epiweeks")

    locations = extract_strings("locations")
    epiweeks = extract_integers("epiweeks")

    # build query
    q = QueryBuilder("gft", "g")

    fields_string = ["location"]
    fields_int = ["epiweek", "num"]
    fields_float = []
    q.set_fields(fields_string, fields_int, fields_float)
    q.set_order("epiweek", "location")

    # build the filter
    q.where_integers("epiweek", epiweeks)
    q.where_strings("location", locations)

    # send query
    return execute_query(str(q), q.params, fields_string, fields_int, fields_float)
