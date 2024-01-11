from flask import Blueprint, request

from .._params import extract_integer, extract_integers, extract_strings
from .._query import execute_query, QueryBuilder
from .._validate import require_all

bp = Blueprint("flusurv", __name__)


@bp.route("/", methods=("GET", "POST"))
def handle():
    require_all(request, "epiweeks", "locations")

    epiweeks = extract_integers("epiweeks")
    locations = extract_strings("locations")
    issues = extract_integers("issues")
    lag = extract_integer("lag")

    # basic query info
    q = QueryBuilder("flusurv", "fs")

    fields_string = ["release_date", "location", "season"]
    fields_int = ["issue", "epiweek", "lag"]
    fields_float = [
        "rate_age_0",
        "rate_age_1",
        "rate_age_2",
        "rate_age_3",
        "rate_age_4",
        "rate_overall",

        "rate_age_5",
        "rate_age_6",
        "rate_age_7",

        "rate_age_18t29",
        "rate_age_30t39",
        "rate_age_40t49",
        "rate_age_5t11",
        "rate_age_12t17",
        "rate_age_lt18",
        "rate_age_gte18",

        "rate_race_white",
        "rate_race_black",
        "rate_race_hisp",
        "rate_race_asian",
        "rate_race_natamer",

        "rate_sex_male",
        "rate_sex_female",
    ]
    q.set_fields(fields_string, fields_int, fields_float)
    q.set_sort_order("epiweek", "location", "issue")

    q.where_integers("epiweek", epiweeks)
    q.where_strings("location", locations)

    if issues is not None:
        q.where_integers("issue", issues)
    elif lag is not None:
        q.where(lag=lag)
    else:
        q.with_max_issue("epiweek", "location")

    # send query
    return execute_query(str(q), q.params, fields_string, fields_int, fields_float)
