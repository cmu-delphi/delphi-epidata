from flask import Blueprint

from .._query import execute_query, QueryBuilder
from .._validate import extract_integer, extract_integers, extract_strings, require_all

# first argument is the endpoint name
bp = Blueprint("paho_dengue", __name__)
required_role = None
alias = None


@bp.route("/", methods=("GET", "POST"))
def handle():
    require_all("regions", "epiweeks")
    regions = extract_strings("regions")
    epiweeks = extract_integers("epiweeks")
    issues = extract_integers("issues")
    lag = extract_integer("lag")

    # build query
    q = QueryBuilder("paho_dengue", "pd")

    fields_string = ["release_date", "region", "serotype"]
    fields_int = [
        "issue",
        "epiweek",
        "lag",
        "total_pop",
        "num_dengue",
        "num_severe",
        "num_deaths",
    ]
    fields_float = ["incidence_rate"]
    q.set_fields(fields_string, fields_int, fields_float)

    q.set_order(epiweek=True, region=True, issue=True)

    # build the filter
    q.where_integers("epiweek", epiweeks)
    q.where_strings("region", regions)

    if issues:
        q.where_integers("issue", issues)
    elif lag is not None:
        q.where(lag=lag)
    else:
        # final query using most recent issues
        q.with_max_issue('epiweek', 'region')

    # send query
    return execute_query(str(q), q.params, fields_string, fields_int, fields_float)
