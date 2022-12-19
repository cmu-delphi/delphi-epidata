from flask import Blueprint

from .._query import execute_query, QueryBuilder
from .._params import (
    extract_integers,
    extract_strings,
)
from .._validate import require_all

# first argument is the endpoint name
bp = Blueprint("gft", __name__)
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
    q.set_select_fields(fields_string, fields_int, fields_float)
    q.set_sort_order("epiweek", "location")

    # build the filter
    q.apply_integer_filters("epiweek", epiweeks)
    q.apply_string_filters("location", locations)

    # send query
    return execute_query(str(q), q.params, fields_string, fields_int, fields_float)
