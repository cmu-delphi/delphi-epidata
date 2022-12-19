from flask import Blueprint

from .._query import execute_query, QueryBuilder
from .._params import (
    extract_integer,
    extract_integers,
    extract_strings,
)
from .._validate import require_all

bp = Blueprint("fluview_clinical", __name__)


@bp.route("/", methods=("GET", "POST"))
def handle():
    require_all("epiweeks", "regions")

    epiweeks = extract_integers("epiweeks")
    regions = extract_strings("regions")
    issues = extract_integers("issues")
    lag = extract_integer("lag")

    # basic query info
    q = QueryBuilder("fluview_clinical", "fvc")

    fields_string = ["release_date", "region"]
    fields_int = ["issue", "epiweek", "lag", "total_specimens", "total_a", "total_b"]
    fields_float = ["percent_positive", "percent_a", "percent_b"]
    q.set_select_fields(fields_string, fields_int, fields_float)
    q.set_sort_order("epiweek", "region", "issue")

    q.apply_integer_filters("epiweek", epiweeks)
    q.apply_string_filters("region", regions)

    if issues is not None:
        q.apply_integer_filters("issue", issues)
    elif lag is not None:
        q.apply_filter(lag=lag)
    else:
        # final query using most recent issues
        q.use_most_recent_issue("epiweek", "region")

    # send query
    return execute_query(str(q), q.params, fields_string, fields_int, fields_float)
