from typing import Any, Dict, List, Tuple

from flask import Blueprint, request

from .._params import extract_integer, extract_integers, extract_strings
from .._query import execute_queries, filter_integers, filter_strings
from .._security import current_user
from .._validate import require_all

# first argument is the endpoint name
bp = Blueprint("fluview", __name__)
alias = None


@bp.route("/", methods=("GET", "POST"))
def handle():
    authorized = False if not current_user else current_user.has_role("fluview")

    require_all(request, "epiweeks", "regions")

    epiweeks = extract_integers("epiweeks")
    regions = extract_strings("regions")
    issues = extract_integers("issues")
    lag = extract_integer("lag")

    # basic query info
    table = "`fluview` fv"
    fields = "fv.`release_date`, fv.`issue`, fv.`epiweek`, fv.`region`, fv.`lag`, fv.`num_ili`, fv.`num_patients`, fv.`num_providers`, fv.`wili`, fv.`ili`, fv.`num_age_0`, fv.`num_age_1`, fv.`num_age_2`, fv.`num_age_3`, fv.`num_age_4`, fv.`num_age_5`"

    queries: List[Tuple[str, Dict[str, Any]]] = []

    def get_fluview_by_table(table: str, fields: str, regions: List[str]):
        # a helper function to query `fluview` and `fluview_imputed` individually
        # parameters
        # basic query info
        order = "fv.`epiweek` ASC, fv.`region` ASC, fv.`issue` ASC"
        params: Dict[str, Any] = dict()
        # build the epiweek filter
        condition_epiweek = filter_integers("fv.`epiweek`", epiweeks, "epiweek", params)
        # build the region filter
        condition_region = filter_strings("fv.`region`", regions, "region", params)
        if issues:
            # build the issue filter
            condition_issue = filter_integers("fv.`issue`", issues, "issues", params)
            # final query using specific issues
            query = f"SELECT {fields} FROM {table} WHERE ({condition_epiweek}) AND ({condition_region}) AND ({condition_issue}) ORDER BY {order}"
        elif lag is not None:
            # build the lag filter
            condition_lag = "(fv.`lag` = :lag)"
            params["lag"] = lag
            # final query using lagged issues
            query = f"SELECT {fields} FROM {table} WHERE ({condition_epiweek}) AND ({condition_region}) AND ({condition_lag}) ORDER BY {order}"
        else:
            # final query using most recent issues
            subquery = f"(SELECT max(`issue`) `max_issue`, `epiweek`, `region` FROM {table} WHERE ({condition_epiweek}) AND ({condition_region}) GROUP BY `epiweek`, `region`) x"
            condition = "x.`max_issue` = fv.`issue` AND x.`epiweek` = fv.`epiweek` AND x.`region` = fv.`region`"
            query = f"SELECT {fields} FROM {table} JOIN {subquery} ON {condition} ORDER BY {order}"

        return query, params

    queries.append(get_fluview_by_table(table, fields, regions))
    if not authorized:
        # Make a special exception for New York. It is a (weighted) sum of two
        # constituent locations -- "ny_minus_jfk" and "jfk" -- both of which are
        # publicly available.
        if "ny" in {r.lower() for r in regions}:
            regions = ["ny"]
            authorized = True

    if authorized:
        # private data (no release date, no age groups, and wili is equal to ili)
        table = "`fluview_imputed` fv"
        fields = "NULL `release_date`, fv.`issue`, fv.`epiweek`, fv.`region`, fv.`lag`, fv.`num_ili`, fv.`num_patients`, fv.`num_providers`, fv.`ili` `wili`, fv.`ili`, NULL `num_age_0`, NULL `num_age_1`, NULL `num_age_2`, NULL `num_age_3`, NULL `num_age_4`, NULL `num_age_5`"
        queries.append(get_fluview_by_table(table, fields, regions))

    fields_string = ["release_date", "region"]
    fields_int = [
        "issue",
        "epiweek",
        "lag",
        "num_ili",
        "num_patients",
        "num_providers",
        "num_age_0",
        "num_age_1",
        "num_age_2",
        "num_age_3",
        "num_age_4",
        "num_age_5",
    ]
    fields_float = ["wili", "ili"]

    # send query
    return execute_queries(queries, fields_string, fields_int, fields_float)
