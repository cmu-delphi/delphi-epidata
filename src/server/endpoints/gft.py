from flask import Blueprint

from .._query import execute_query, QueryBuilder
from .._validate import extract_integers, extract_strings, require_all

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
    q.fields = "g.epiweek, g.location, g.num"
    q.order = "g.epiweek ASC, g.location ASC"

    # build the filter
    q.where_integers("epiweek", epiweeks)
    q.where_strings("location", locations)

    fields_string = ["location"]
    fields_int = ["epiweek", "num"]
    fields_float = []

    # send query
    return execute_query(str(q), q.params, fields_string, fields_int, fields_float)
