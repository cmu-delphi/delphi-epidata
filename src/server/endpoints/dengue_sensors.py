from flask import Blueprint

from .._config import AUTH
from .._params import extract_integers, extract_strings
from .._query import execute_query, QueryBuilder
from .._validate import check_auth_token, require_all

# first argument is the endpoint name
bp = Blueprint("dengue_sensors", __name__)
alias = None


@bp.route("/", methods=("GET", "POST"))
def handle():
    check_auth_token(AUTH["sensors"])
    require_all("names", "locations", "epiweeks")

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
