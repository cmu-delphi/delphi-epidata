from flask import Blueprint

from .._query import execute_query, filter_integers, filter_strings
from .._validate import extract_integer, extract_integers, extract_strings, require_all

# first argument is the endpoint name
bp = Blueprint("nidss_flu", __name__)
alias = None


@bp.route("/", methods=("GET", "POST"))
def handle():
    require_all("regions", "epiweeks")
    regions = extract_strings("regions")
    epiweeks = extract_integers("epiweeks")
    issues = extract_integers("issues")
    lag = extract_integer("lag")

    # build query
    table = "`nidss_flu` nf"
    fields = "nf.`release_date`, nf.`issue`, nf.`epiweek`, nf.`region`, nf.`lag`, nf.`visits`, nf.`ili`"
    order = "nf.`epiweek` ASC, nf.`region` ASC, nf.`issue` ASC"
    # build the filter
    params = dict()
    # build the epiweek filter
    condition_epiweek = filter_integers("nf.`epiweek`", epiweeks, "epiweek", params)
    # build the region filter
    condition_region = filter_strings("nf.`region`", regions, "region", params)
    if issues:
        condition_issue = filter_integers("nf.`issue`", issues, "issue", params)
        # final query using specific issues
        query = f"SELECT {fields} FROM {table} WHERE ({condition_epiweek}) AND ({condition_region}) AND ({condition_issue}) ORDER BY {order}"
    elif lag is not None:
        # build the lag filter
        condition_lag = "(nf.`lag` = :lag)"
        params["lag"] = lag
        # final query using lagged issues
        query = f"SELECT {fields} FROM {table} WHERE ({condition_epiweek}) AND ({condition_region}) AND ({condition_lag}) ORDER BY {order}"
    else:
        # final query using most recent issues
        subquery = f"(SELECT max(`issue`) `max_issue`, `epiweek`, `region` FROM {table} WHERE ({condition_epiweek}) AND ({condition_region}) GROUP BY `epiweek`, `region`) x"
        condition = "x.`max_issue` = nf.`issue` AND x.`epiweek` = nf.`epiweek` AND x.`region` = nf.`region`"
        query = f"SELECT {fields} FROM {table} JOIN {subquery} ON {condition} ORDER BY {order}"

    fields_string = ["release_date", "region"]
    fields_int = ["issue", "epiweek", "lag", "visits"]
    fields_float = ["ili"]

    # send query
    return execute_query(query, params, fields_string, fields_int, fields_float)
