from flask import jsonify, request, Blueprint

from sqlalchemy import select
from .._common import app, db
from .._config import AUTH
from .._validate import require_all, extract_strings, extract_integers
from .._query import filter_strings, execute_query, filter_integers
from .._exceptions import UnAuthenticatedException

# first argument is the endpoint name
bp = Blueprint("gft", __name__)
alias = None


@bp.route("/", methods=("GET", "POST"))
def handle():
    require_all("locations", "epiweeks")

    locations = extract_strings("locations")
    epiweeks = extract_integers("epiweeks")

    # build query
    table = "`gft` g"
    fields = "g.`epiweek`, g.`location`, g.`num`"
    order = "g.`epiweek` ASC, g.`location` ASC"

    # build the filter
    params = dict()
    condition_epiweek = filter_integers("g.`epiweek`", epiweeks, "epiweek", params)
    # build the location filter
    condition_location = filter_strings("g.`location`", locations, "loc", params)
    # the query
    query = f"SELECT {fields} FROM {table} WHERE ({condition_epiweek}) AND ({condition_location}) ORDER BY {order}"

    fields_string = [
        "location",
    ]
    fields_int = ["epiweek", "num"]
    fields_float = []

    # send query
    return execute_query(query, params, fields_string, fields_int, fields_float)
