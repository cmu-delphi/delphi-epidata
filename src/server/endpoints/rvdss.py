from flask import Blueprint, request

from .._params import (
    extract_date,
    extract_dates,
    extract_strings,
    parse_time_set,
)
from .._query import execute_query, QueryBuilder
from .._validate import require_all

bp = Blueprint("rvdss", __name__)

db_table_name = "rvdss"

@bp.route("/", methods=("GET", "POST"))
def handle():
    require_all(request, "time_type", "time_values", "geo_type", "geo_values")

    time_set = parse_time_set()
    geo_type = extract_strings("geo_type")
    geo_values = extract_strings("geo_values")
    issues = extract_dates("issues")
    as_of = extract_date("as_of")

    # basic query info
    q = QueryBuilder(db_table_name, "rv")

    fields_string = [
        "geo_type",
        "geo_value",
        "time_type",
    ]
    fields_int = [
        "epiweek",
        "time_value",
        "issue",
        "year",
    ]
    fields_float = [
        "adv_pct_positive",
        "adv_positive_tests",
        "adv_tests",
        "evrv_pct_positive",
        "evrv_positive_tests",
        "evrv_tests",
        "flu_pct_positive",
        "flu_positive_tests",
        "flu_tests",
        "flua_pct_positive",
        "flua_positive_tests",
        "flua_tests",
        "fluah1n1pdm09_positive_tests",
        "fluah3_positive_tests",
        "fluauns_positive_tests",
        "flub_pct_positive",
        "flub_positive_tests",
        "flub_tests",
        "hcov_pct_positive",
        "hcov_positive_tests",
        "hcov_tests",
        "hmpv_pct_positive",
        "hmpv_positive_tests",
        "hmpv_tests",
        "hpiv1_positive_tests",
        "hpiv2_positive_tests",
        "hpiv3_positive_tests",
        "hpiv4_positive_tests",
        "hpiv_pct_positive",
        "hpiv_positive_tests",
        "hpiv_tests",
        "hpivother_positive_tests",
        "rsv_pct_positive",
        "rsv_positive_tests",
        "rsv_tests",
        "sarscov2_pct_positive",
        "sarscov2_positive_tests",
        "sarscov2_tests",
    ]

    q.set_sort_order("epiweek", "time_value", "geo_type", "geo_value", "issue")
    q.set_fields(fields_string, fields_int, fields_float)

    q.where_strings("geo_type", geo_type)
    # Only apply geo_values filter if wildcard "*" was NOT used.
    if not (len(geo_values) == 1 and geo_values[0] == "*"):
        q.where_strings("geo_value", geo_values)

    q.apply_time_filter("time_type", "time_value", time_set)
    q.apply_issues_filter(db_table_name, issues)
    q.apply_as_of_filter(db_table_name, as_of, use_source_signal = False)

    # send query
    return execute_query(str(q), q.params, fields_string, fields_int, fields_float)
