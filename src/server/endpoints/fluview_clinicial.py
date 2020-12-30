from flask import jsonify, request, Blueprint

from sqlalchemy import select
from .._common import app, db
from .._config import AUTH
from .._validate import require_all, extract_strings, extract_integers, extract_integer
from .._query import filter_strings, execute_query, filter_integers, execute_queries

bp = Blueprint("fluview_clinical", __name__)


@bp.route("/", methods=("GET", "POST"))
def handle():
    require_all("epiweeks", "regions")

    epiweeks = extract_integers("epiweeks")
    regions = extract_strings("regions")
    issues = extract_integers("issues")
    lag = extract_integer("lag")

    # basic query info
    table = "`fluview_clinical` fvc"
    fields = "fvc.`release_date`, fvc.`issue`, fvc.`epiweek`, fvc.`region`, fvc.`lag`, fvc.`total_specimens`, fvc.`total_a`, fvc.`total_b`, fvc.`percent_positive`, fvc.`percent_a`, fvc.`percent_b`"
    order = "fvc.`epiweek` ASC, fvc.`region` ASC, fvc.`issue` ASC"

    params = dict()
    # build the epiweek filter
    condition_epiweek = filter_integers("fs.`epiweek`", epiweeks, "epiweek", params)
    # build the location filter
    condition_region = filter_strings("fs.`region`", regions, "regions", params)
    if issues is not None:
        # build the issue filter
        condition_issue = filter_integers("fvc.`issue`", issues, "issue", params)
        # final query using specific issues
        query = f"SELECT {fields} FROM {table} WHERE ({condition_epiweek}) AND ({condition_region}) AND ({condition_issue}) ORDER BY {order}"
    elif lag is not None:
        # build the lag filter
        condition_lag = "(fvc.`lag` = :lag)"
        params["lag"] = lag
        # final query using lagged issues
        query = f"SELECT {fields} FROM {table} WHERE ({condition_epiweek}) AND ({condition_region}) AND ({condition_lag}) ORDER BY {order}"
    else:
        # final query using most recent issues
        subquery = f"(SELECT max(`issue`) `max_issue`, `epiweek`, `region` FROM {table} WHERE ({condition_epiweek}) AND ({condition_region}) GROUP BY `epiweek`, `region`) x"
        condition = "x.`max_issue` = fvc.`issue` AND x.`epiweek` = fvc.`epiweek` AND x.`region` = fvc.`region`"
        query = f"SELECT {fields} FROM {table} JOIN {subquery} ON {condition} ORDER BY {order}"

    fields_string = ["release_date", "region"]
    fields_int = ["issue", "epiweek", "lag", "total_specimens", "total_a", "total_b"]
    fields_float = ["percent_positive", "percent_a", "percent_b"]

    # send query
    return execute_query(query, params, fields_string, fields_int, fields_float)
