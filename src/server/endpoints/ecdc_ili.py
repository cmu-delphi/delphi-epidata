from flask import Blueprint, request

from .._params import extract_integer, extract_integers, extract_strings
from .._query import execute_query, QueryBuilder
from .._validate import require_all

# first argument is the endpoint name
bp = Blueprint("ecdc_ili", __name__)
alias = None


@bp.route("/", methods=("GET", "POST"))
def handle():
    require_all(request, "regions", "epiweeks")
    regions = extract_strings("regions")
    epiweeks = extract_integers("epiweeks")
    issues = extract_integers("issues")
    lag = extract_integer("lag")

    # build query
    q = QueryBuilder("ecdc_ili", "ec")

    fields_string = ["release_date", "region"]
    fields_int = ["issue", "epiweek", "lag"]
    fields_float = ["incidence_rate"]
    q.set_fields(fields_string, fields_int, fields_float)

    q.set_sort_order("epiweek", "region", "issue")

    q.where_integers("epiweek", epiweeks)
    q.where_strings("region", regions)

    if issues is not None:
        q.where_integers("issue", issues)
    elif lag is not None:
        q.where(lag=lag)
    else:
        q.with_max_issue("epiweek", "region")

    # send query
    return execute_query(str(q), q.params, fields_string, fields_int, fields_float)
