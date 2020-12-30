from flask import jsonify, request, Blueprint
import re

from sqlalchemy import select
from .._common import app, db
from .._config import AUTH
from .._validate import require_all, extract_strings, extract_integers, extract_integer
from .._query import filter_strings, execute_query, filter_integers, execute_queries


# first argument is the endpoint name
bp = Blueprint("ecdc_ili", __name__)
alias = None


@bp.route("/", methods=("GET", "POST"))
def handle():
    require_all("regions", "epiweeks")
    regions = extract_strings("regions")
    epiweeks = extract_integers("epiweeks")
    issues = extract_integers("issues")
    lag = extract_integer("lag")

    # build query
    table = "`ecdc_ili` ec"
    fields = "ec.`release_date`, ec.`issue`, ec.`epiweek`, ec.`region`, ec.`lag`, ec.`incidence_rate`"
    order = "ec.`epiweek` ASC, ec.`region` ASC, ec.`issue` ASC"
    # build the filter
    params = dict()
    # build the epiweek filter
    condition_epiweek = filter_integers("ec.`epiweek`", epiweeks, "epiweek", params)
    # build the region filter
    condition_region = filter_strings("ec.`region`", regions, "region", params)
    if issues:
        condition_issue = filter_integers("ec.`issue`", issues, "issue", params)
        # final query using specific issues
        query = f"SELECT {fields} FROM {table} WHERE ({condition_epiweek}) AND ({condition_region}) AND ({condition_issue}) ORDER BY {order}"
    elif lag is not None:
        # build the lag filter
        condition_lag = "(ec.`lag` = :lag)"
        params["lag"] = lag
        # final query using lagged issues
        query = f"SELECT {fields} FROM {table} WHERE ({condition_epiweek}) AND ({condition_region}) AND ({condition_lag}) ORDER BY {order}"
    else:
        # final query using most recent issues
        subquery = f"(SELECT max(`issue`) `max_issue`, `epiweek`, `region` FROM {table} WHERE ({condition_epiweek}) AND ({condition_region}) GROUP BY `epiweek`, `region`) x"
        condition = "x.`max_issue` = ec.`issue` AND x.`epiweek` = ec.`epiweek` AND x.`region` = ec.`region`"
        query = f"SELECT {fields} FROM {table} JOIN {subquery} ON {condition} ORDER BY {order}"

    fields_string = [
        "release_date",
        "region",
    ]
    fields_int = ["issue", "epiweek", "lag"]
    fields_float = ["incidence_rate"]

    # send query
    return execute_query(query, params, fields_string, fields_int, fields_float)
