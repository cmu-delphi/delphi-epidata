from flask import Blueprint, request

from .._config import NATION_REGION, REGION_TO_STATE
from .._query import execute_queries, filter_dates, filter_integers, filter_strings
from .._validate import (
    extract_integers,
    extract_strings,
    require_all,
    require_any,
)
from .._security import require_role

# first argument is the endpoint name
bp = Blueprint("twitter", __name__)
alias = None


@bp.route("/", methods=("GET", "POST"))
@require_role("twitter")
def handle():
    require_all("locations")
    require_any("dates", "epiweeks")

    locations = extract_strings("locations")
    if "dates" in request.values:
        resolution = "daily"
        dates = extract_integers("dates")
    else:
        resolution = "weekly"
        dates = extract_integers("epiweeks")

    # build query
    table = "`twitter` t"
    params = dict()

    fields_string = ["location"]
    fields_int = ["num", "total"]
    fields_float = ["percent"]

    if resolution == "daily":
        date_field = "t.`date`"
        date_name = "date"
        condition_date = filter_dates(date_field, dates, "date", params)
        fields_string.append(date_name)
    else:
        date_field = "yearweek(t.`date`, 6)"
        date_name = "epiweek"
        condition_date = filter_integers(date_field, dates, "epiweek", params)
        fields_int.append(date_name)

    fields = f"{date_field} `{date_name}`, sum(t.`num`) `num`, sum(t.`total`) `total`, round(100 * sum(t.`num`) / sum(t.`total`), 8) `percent`"

    # for consistency (some rows have low `total`, or `num` > `total`), filter out 2% of rows with highest `percent`
    condition_filter = "t.`num` / t.`total` <= 0.019"

    # split locations into national/regional/state
    regions = []
    states = []
    for location in locations:
        location = location.lower()
        if location == NATION_REGION or location in REGION_TO_STATE:
            regions.append(location)
        else:
            states.append(location)

    queries = []
    # query each region type individually (the data is stored by state, so getting regional data requires some extra processing)
    for region in regions:
        assert region == NATION_REGION or region in REGION_TO_STATE
        # escape region not needed since only certain valid strings
        region_params = params.copy()
        if region == NATION_REGION:
            # final query for U.S. National
            query = f"SELECT {fields}, '{region}' `location` FROM {table} WHERE ({condition_filter}) AND ({condition_date}) GROUP BY {date_field} ORDER BY {date_field} ASC"
        else:
            # build the location filter
            condition_location = "`state` IN :region_states"
            region_params["region_states"] = REGION_TO_STATE[region]
            # final query for HHS Regions
            query = f"SELECT {fields}, '{region}' `location` FROM {table} WHERE ({condition_filter}) AND ({condition_date}) AND ({condition_location}) GROUP BY {date_field} ORDER BY {date_field} ASC"

        queries.append((query, region_params))

    # query all states together
    if states:
        # build the location filter
        state_params = params.copy()
        condition_location = filter_strings("t.`state`", states, "state", state_params)
        # final query for states
        query = f"SELECT {fields}, t.`state` `location` FROM {table} WHERE ({condition_filter}) AND ({condition_date}) AND ({condition_location}) GROUP BY {date_field}, t.`state` ORDER BY {date_field} ASC, t.`state` ASC"
        # append query results to the epidata array
        queries.append((query, state_params))

    # send query
    return execute_queries(queries, fields_string, fields_int, fields_float)
