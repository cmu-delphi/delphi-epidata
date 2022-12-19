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

    fields_string = ["release_date", "region"]
    fields_int = ["issue", "epiweek", "lag"]
    fields_float = ["ili"]
    q.set_select_fields(fields_string, fields_int, fields_float)

    q.set_sort_order("epiweek", "region", "issue")
    # build the filter
    q.apply_integer_filters("epiweek", epiweeks)
    q.apply_string_filters("region", regions)

    if issues:
        q.apply_integer_filters("issue", issues)
    elif lag is not None:
        q.apply_filter(lag=lag)
    else:
        q.use_most_recent_issue('epiweek', 'region')

    # send query
    return execute_query(str(q), q.params, fields_string, fields_int, fields_float)
