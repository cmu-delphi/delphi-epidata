from flask import Blueprint

from .._query import execute_query, QueryBuilder
from .._validate import extract_integer, extract_integers, extract_strings, require_all

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
    q.fields = "fvc.release_date, fvc.issue, fvc.epiweek, fvc.region, fvc.lag, fvc.total_specimens, fvc.total_a, fvc.total_b, fvc.percent_positive, fvc.percent_a, fvc.percent_b"
    q.order = "fvc.epiweek ASC, fvc.region ASC, fvc.issue ASC"

    q.where_integers("epiweek", epiweeks)
    q.where_strings("region", regions)

    if issues is not None:
        q.where_integers("issue", issues)
    elif lag is not None:
        q.where(lag=lag)
    else:
        # final query using most recent issues
        condition = "x.max_issue = fvc.issue AND x.epiweek = fvc.epiweek AND x.region = fvc.region"
        q.subquery = f"JOIN (SELECT max(issue) max_issue, epiweek, region FROM {q.table} WHERE {q.conditions_clause} GROUP BY epiweek, region) x ON {condition}"

    fields_string = ["release_date", "region"]
    fields_int = ["issue", "epiweek", "lag", "total_specimens", "total_a", "total_b"]
    fields_float = ["percent_positive", "percent_a", "percent_b"]

    # send query
    return execute_query(str(q), q.params, fields_string, fields_int, fields_float)
