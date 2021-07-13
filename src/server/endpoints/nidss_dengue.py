import re

from flask import Blueprint

from .._query import execute_queries, filter_integers
from .._validate import extract_integers, extract_strings, require_all

# first argument is the endpoint name
bp = Blueprint("nidss_dengue", __name__)
required_role = None
alias = None


@bp.route("/", methods=("GET", "POST"))
def handle():
    require_all("locations", "epiweeks")
    locations = extract_strings("locations")
    epiweeks = extract_integers("epiweeks")

    # build query
    # build the filter
    params = dict()
    # build the epiweek filter
    condition_epiweek = filter_integers("nd.`epiweek`", epiweeks, "epiweek", params)

    queries = []
    for location in locations:
        # some kind of enforcing escaping
        location = re.search(r"([\w-]+)", location)[0]
        location_params = params.copy()
        query = f"""
            SELECT
                nd2.`epiweek`, nd2.`location`, count(1) `num_locations`, sum(nd2.`count`) `count`
            FROM (
                SELECT
                nd1.`epiweek`, CASE WHEN q.`query` = nd1.`location` THEN nd1.`location` WHEN q.`query` = nd1.`region` THEN nd1.`region` ELSE nd1.`nat` END `location`, nd1.`count`
                FROM (
                SELECT
                    `epiweek`, `location`, `region`, 'nationwide' `nat`, `count`
                FROM
                    `nidss_dengue` nd
                WHERE {condition_epiweek}
                ) nd1
                JOIN (
                SELECT
                    '{location}' `query`
                ) q
                ON
                q.`query` IN (nd1.`location`, nd1.`region`, nd1.`nat`)
            ) nd2
            GROUP BY
                nd2.`epiweek`, nd2.`location`
            """
        queries.append((query, location_params))

    fields_string = ["location"]
    fields_int = ["epiweek", "count"]
    fields_float = []

    # send query
    return execute_queries(queries, fields_string, fields_int, fields_float)
