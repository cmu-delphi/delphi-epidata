from flask import Blueprint, request

from .._params import extract_integers, extract_strings, extract_date, extract_dates
from .._query import execute_query, QueryBuilder
from .._validate import require_all

bp = Blueprint("rvdss", __name__)

db_table_name = "rvdss"

def parse_time_set_epiweeks() -> TimeSet:
    require_all(request, "epiweeks")
    time_values = extract_dates("epiweeks")
    if time_values == ["*"]:
        return TimeSet("week", True)
    return TimeSet("week", time_values)

    return parse_time_arg()


@bp.route("/", methods=("GET", "POST"))
def handle():
    require_all(request, "epiweeks", "geo_type", "geo_values")

    # epiweeks = extract_integers("epiweeks")
    time_set = parse_time_set_epiweeks()
    geo_sets = parse_geo_sets()
    # issues = extract_integers("issues") # TODO
    issues = extract_dates("issues")
    # as_of = extract_date("as_of")

    # basic query info
    q = QueryBuilder(db_table_name, "rv")

    fields_string = [
        "geo_type",
        "geo_value",
        "region",
    ]
    fields_int = [
        "epiweek",
        "week",
        "weekorder",
        "year",
        "time_value",
        "issue",
    ]
    fields_float = [
        "sarscov2_tests",
        "sarscov2_positive_tests",
        "sarscov2_pct_positive",
        "flu_tests",
        "flua_tests",
        "flub_tests",
        "flu_positive_tests",
        "flu_pct_positive",
        "fluah1n1pdm09_positive_tests",
        "fluah3_positive_tests",
        "fluauns_positive_tests",
        "flua_positive_tests",
        "flua_pct_positive",
        "flub_positive_tests",
        "flub_pct_positive",
        "rsv_tests",
        "rsv_positive_tests",
        "rsv_pct_positive",
        "hpiv_tests",
        "hpiv1_positive_tests",
        "hpiv2_positive_tests",
        "hpiv3_positive_tests",
        "hpiv4_positive_tests",
        "hpivother_positive_tests",
        "hpiv_positive_tests",
        "hpiv_pct_positive",
        "adv_tests",
        "adv_positive_tests",
        "adv_pct_positive",
        "hmpv_tests",
        "hmpv_positive_tests",
        "hmpv_pct_positive",
        "evrv_tests",
        "evrv_positive_tests",
        "evrv_pct_positive",
        "hcov_tests",
        "hcov_positive_tests",
        "hcov_pct_positive",
    ]

    q.set_sort_order("epiweek", "time_value" "geo_type", "geo_value", "issue")
    q.set_fields(fields_string, fields_int, fields_float)

    # q.where_strings("geo_type", geo_type)
    q.apply_geo_filters("geo_type", "geo_value", geo_sets)
    # TODO: can only use this if have a time_type field in data
    # q.apply_time_filter("time_type", "time_value", time_set)
    q.where_integers("epiweek", epiweeks)

    q.apply_issues_filter(db_table_name, issues)
    # TODO: can only use this if have a time_type field in data
    # q.apply_as_of_filter(db_table_name, as_of, use_source_signal = FALSE)

    # if issues is not None:
    #     q.where_integers("issue", issues)
    # else:
    #     q.with_max_issue("epiweek", "geo_value")

    # send query
    return execute_query(str(q), q.params, fields_string, fields_int, fields_float)
