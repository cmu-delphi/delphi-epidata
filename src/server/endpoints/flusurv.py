from flask import Blueprint

from .._params import extract_integer, extract_integers, extract_strings
from .._query import execute_query, QueryBuilder
from .._validate import require_all

bp = Blueprint("flusurv", __name__)


@bp.route("/", methods=("GET", "POST"))
def handle():
    require_all("epiweeks", "locations")

    epiweeks = extract_integers("epiweeks")
    locations = extract_strings("locations")
    issues = extract_integers("issues")
    lag = extract_integer("lag")

    # basic query info
    q = QueryBuilder("flusurv", "fs")

    fields_string = ["release_date", "location"]
    fields_int = ["issue", "epiweek", "lag"]
    fields_float = [
        "rate_age_0",
        "rate_age_1",
        "rate_age_2",
        "rate_age_3",
        "rate_age_4",
        "rate_overall",
    ]
    q.set_fields(fields_string, fields_int, fields_float)
    q.set_sort_order("epiweek", "location", "issue")

    q.where_integers("epiweek", epiweeks)
    q.where_strings("location", locations)

    if issues is not None:
        q.where_integers("issue", issues)
    elif lag is not None:
        q.where(lag=lag)
    else:
        q.with_max_issue("epiweek", "location")

    # send query
    return execute_query(str(q), q.params, fields_string, fields_int, fields_float)
