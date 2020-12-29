from flask import jsonify, request, Blueprint

from sqlalchemy import select
from .._common import app, db
from .._config import AUTH
from .._validate import require_any, extract_strings, extract_ints
from .._query import filter_strings, execute_query

# first argument is the endpoint name
bp = Blueprint("covid_hosp_facility_lookup", __name__)


@bp.route("/", methods=("GET", "POST"))
def handle():
    require_any("state")
    state = extract_strings("state")

    # build query
    table = "TABLE c"
    fields = ", ".join([])
    # basic query info
    group = "c.`hospital_pk`"
    order = "c.`hospital_pk` ASC"
    # build the filter
    # these are all fast because the table has indexes on each of these fields
    condition = "FALSE"
    params = dict()
    if state:
        condition = filter_strings("c.`state`", state, "state", params)

    # final query using specific issues
    query = f"SELECT {fields} FROM {table} WHERE ({condition}) GROUP BY {group} ORDER BY {order}"

    fields_string = [
        "hospital_pk",
        "fips_code",
    ]
    fields_int = ["is_metro_micro"]
    fields_float = []

    # send query
    return execute_query(query, params, fields_string, fields_int, fields_float)
