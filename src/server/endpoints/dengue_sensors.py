from flask import jsonify, request, Blueprint

from sqlalchemy import select
from .._common import app, db
from .._config import AUTH, NATION_REGION, REGION_TO_STATE
from .._validate import require_all, extract_strings, extract_integers
from .._query import filter_strings, execute_queries, filter_integers
from .._exceptions import UnAuthenticatedException

# first argument is the endpoint name
bp = Blueprint("dengue_sensors", __name__)
alias = None


@bp.route("/", methods=("GET", "POST"))
def handle():
    require_all("auth", "names", "locations", "epiweeks")
    if request.values["auth"] != AUTH["sensors"]:
        raise UnAuthenticatedException()

    names = extract_strings("names")
    locations = extract_strings("locations")
    epiweeks = extract_integers("epiweeks")

    # build query
    table = "`cdc_extract` c"
    group = "c.`epiweek`"
    order = "c.`epiweek` ASC"
    params = dict()

    # build the epiweek filter
    condition_epiweek = filter_integers("c.`epiweek`", epiweeks, "epiweek", params)
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
        assert location == NATION_REGION or location in REGION_TO_STATE
        # escape region not needed since only certain valid strings
        fields = f"'{region}' `location`, c.`epiweek`, sum(c.`num1`) `num1`, sum(c.`num2`) `num2`, sum(c.`num3`) `num3`, sum(c.`num4`) `num4`, sum(c.`num5`) `num5`, sum(c.`num6`) `num6`, sum(c.`num7`) `num7`, sum(c.`num8`) `num8`, sum(c.`total`) `total`"
        region_params = params.copy()
        if region == NATION_REGION:
            # final query for U.S. National
            query = f"SELECT {fields} FROM {table} WHERE ({condition_epiweek}) GROUP BY {group} ORDER BY {order}"
        else:
            # build the location filter
            condition_location = "`state` IN :region_states"
            region_params["region_states"] = REGION_TO_STATE[region]
            # final query for HHS Regions
            query = f"SELECT {fields} FROM {table} WHERE ({condition_epiweek}) AND ({condition_location}) GROUP BY {group} ORDER BY {order}"

        queries.append((query, region_params))

    # query all states together
    if states:
        fields = "c.`state` `location`, c.`epiweek`, c.`num1`, c.`num2`, c.`num3`, c.`num4`, c.`num5`, c.`num6`, c.`num7`, c.`num8`, c.`total`"
        # build the location filter
        state_params = params.copy()
        condition_location = filter_strings("c.`state`", states, "state", state_params)
        # final query for states
        query = f"SELECT {fields} FROM {table} WHERE ({condition_epiweek}) AND ({condition_location}) ORDER BY {order}, c.`state` ASC"
        # append query results to the epidata array
        queries.append((query, state_params))

    fields_string = [
        "location",
    ]
    fields_int = [
        "epiweek",
        "num1",
        "num2",
        "num3",
        "num4",
        "num5",
        "num6",
        "num7",
        "num8",
        "total",
    ]
    fields_float = ["value"]

    # send query
    return execute_queries(queries, fields_string, fields_int, fields_float)
