from flask import Blueprint

from .._query import execute_query, QueryBuilder
from .._validate import extract_integers, extract_strings, require_all
from .._security import require_role
from .._config import UserRole

# first argument is the endpoint name
bp = Blueprint("quidel", __name__)
alias = None


@bp.route("/", methods=("GET", "POST"))
@require_role(UserRole.quidel)
def handle():
    require_all("locations", "epiweeks")

    locations = extract_strings("locations")
    epiweeks = extract_integers("epiweeks")

    # build query
    q = QueryBuilder("quidel", "q")

    fields_string = ["location"]
    fields_int = ["epiweek"]
    fields_float = ["value"]
    q.set_fields(fields_string, fields_int, fields_float)

    q.set_order(epiweek=True, location=True)

    # build the filter
    q.where_strings("location", locations)
    q.where_integers("epiweek", epiweeks)

    # send query
    return execute_query(str(q), q.params, fields_string, fields_int, fields_float)
