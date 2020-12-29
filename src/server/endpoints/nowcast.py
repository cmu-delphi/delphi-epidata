from flask import jsonify, request, Blueprint

from sqlalchemy import select
from .._common import app, db
from .._config import AUTH
from .._validate import require_all, extract_strings, extract_integers
from .._query import filter_strings, execute_query, filter_integers

# first argument is the endpoint name
bp = Blueprint("nowcast", __name__)
alias = None


@bp.route("/", methods=("GET", "POST"))
def handle():
    require_all("locations", "epiweeks")
    locations = extract_strings("locations")
    epiweeks = extract_integers("epiweeks")

    # build query
    table = "`nowcasts` n"
    fields = "n.`location`, n.`epiweek`, n.`value`, n.`std`"
    # basic query info
    order = "n.`epiweek` ASC, n.`location` ASC"
    # build the filter
    params = dict()
    # build the location filter
    condition_location = filter_strings("n.`location`", locations, "loc", params)
    # build the epiweek filter
    condition_epiweek = filter_integers("n.`epiweek`", epiweeks, "epiweek", params)
    # the query
    query = f"SELECT {fields} FROM {table} WHERE ({condition_location}) AND ({condition_epiweek}) ORDER BY {order}"

    fields_string = [
        "location",
    ]
    fields_int = ["epiweek"]
    fields_float = ["value", "std"]

    # send query
    return execute_query(query, params, fields_string, fields_int, fields_float)
