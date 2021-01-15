from flask import Blueprint

from .._query import execute_query, QueryBuilder
from .._validate import extract_integer, extract_integers, extract_strings, require_all

# first argument is the endpoint name
bp = Blueprint("kcdc_ili", __name__)
alias = None


@bp.route("/", methods=("GET", "POST"))
def handle():
    require_all("regions", "epiweeks")
    regions = extract_strings("regions")
    epiweeks = extract_integers("epiweeks")
    issues = extract_integers("issues")
    lag = extract_integer("lag")

    # build query
    q = QueryBuilder("kcdc_ili", "kc")
    q.fields = "kc.release_date, kc.issue, kc.epiweek, kc.region, kc.lag, kc.ili"
    q.order = "kc.epiweek ASC, kc.region ASC, kc.issue ASC"
    # build the filter
    q.where_integers("epiweek", epiweeks)
    q.where_strings("region", regions)

    if issues:
        q.where_integers("issue", issues)
    elif lag is not None:
        q.where(lag=lag)
    else:
        # final query using most recent issues
        condition = (
            f"x.max_issue = {q.alias}.issue AND x.epiweek = {q.alias}.epiweek AND x.region = {q.alias}.region"
        )
        q.subquery = f"JOIN (SELECT max(issue) max_issue, epiweek, region FROM {q.table} WHERE {q.conditions_clause} GROUP BY epiweek, region) x ON {condition}"

    fields_string = ["release_date", "region"]
    fields_int = ["issue", "epiweek", "lag"]
    fields_float = ["ili"]

    # send query
    return execute_query(str(q), q.params, fields_string, fields_int, fields_float)
