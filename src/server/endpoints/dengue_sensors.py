from flask import Blueprint, request

from .._params import extract_integers, extract_strings
from .._query import execute_query, QueryBuilder
from .._validate import require_all
from .._security import require_role

# first argument is the endpoint name
bp = Blueprint("dengue_sensors", __name__)
alias = None


@bp.route("/", methods=("GET", "POST"))
@require_role("sensors")
def handle():
    require_all(request, "names", "locations", "epiweeks")

    names = extract_strings("names")
    locations = extract_strings("locations")
    epiweeks = extract_integers("epiweeks")

    # build query
    q = QueryBuilder("dengue_sensors", "s")

    fields_string = ["name", "location"]
    fields_int = ["epiweek"]
    fields_float = ["value"]
    q.set_fields(fields_string, fields_int, fields_float)
    
    q.set_sort_order('epiweek', 'name', 'location')
    
    q.where_strings('name', names)
    q.where_strings('location', locations)
    q.where_integers('epiweek', epiweeks)

    # send query
    return execute_query(str(q), q.params, fields_string, fields_int, fields_float)
