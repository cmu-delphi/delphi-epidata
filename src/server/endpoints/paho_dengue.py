from flask import Blueprint

from .._query import execute_query, filter_integers, filter_strings
from .._validate import extract_integer, extract_integers, extract_strings, require_all

# first argument is the endpoint name
bp = Blueprint("paho_dengue", __name__)
alias = None


@bp.route("/", methods=("GET", "POST"))
def handle():
    require_all("regions", "epiweeks")
    regions = extract_strings("regions")
    epiweeks = extract_integers("epiweeks")
    issues = extract_integers("issues")
    lag = extract_integer("lag")

    # build query
    table = "`paho_dengue` pd"
    fields = "pd.`release_date`, pd.`issue`, pd.`epiweek`, pd.`region`, pd.`lag`, pd.`total_pop`, pd.`serotype`, pd.`num_dengue`, pd.`incidence_rate`, pd.`num_severe`, pd.`num_deaths`"
    order = "pd.`epiweek` ASC, pd.`region` ASC, pd.`issue` ASC"
    # build the filter
    params = dict()
    # build the epiweek filter
    condition_epiweek = filter_integers("pd.`epiweek`", epiweeks, "epiweek", params)
    # build the region filter
    condition_region = filter_strings("pd.`region`", regions, "region", params)
    if issues:
        condition_issue = filter_integers("pd.`issue`", issues, "issue", params)
        # final query using specific issues
        query = f"SELECT {fields} FROM {table} WHERE ({condition_epiweek}) AND ({condition_region}) AND ({condition_issue}) ORDER BY {order}"
    elif lag is not None:
        # build the lag filter
        condition_lag = "(pd.`lag` = :lag)"
        params["lag"] = lag
        # final query using lagged issues
        query = f"SELECT {fields} FROM {table} WHERE ({condition_epiweek}) AND ({condition_region}) AND ({condition_lag}) ORDER BY {order}"
    else:
        # final query using most recent issues
        subquery = f"(SELECT max(`issue`) `max_issue`, `epiweek`, `region` FROM {table} WHERE ({condition_epiweek}) AND ({condition_region}) GROUP BY `epiweek`, `region`) x"
        condition = "x.`max_issue` = pd.`issue` AND x.`epiweek` = pd.`epiweek` AND x.`region` = pd.`region`"
        query = f"SELECT {fields} FROM {table} JOIN {subquery} ON {condition} ORDER BY {order}"

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

    # send query
    return execute_query(query, params, fields_string, fields_int, fields_float)
