from flask import Blueprint

from .._query import execute_query, filter_strings
from .._validate import extract_strings, require_any

# first argument is the endpoint name
bp = Blueprint("covid_hosp_facility_lookup", __name__)


@bp.route("/", methods=("GET", "POST"))
def handle():
    require_any("state", "ccn", "city", "zip", "fips_code")
    state = extract_strings("state")
    ccn = extract_strings("ccn")
    city = extract_strings("city")
    zip = extract_strings("zip")
    fips_code = extract_strings("fips_code")

    # build query
    table = "covid_hosp_facility c"
    fields = ", ".join(
        [
            "c.`hospital_pk`",
            "MAX(c.`state`) `state`",
            "MAX(c.`ccn`) `ccn`",
            "MAX(c.`hospital_name`) `hospital_name`",
            "MAX(c.`address`) `address`",
            "MAX(c.`city`) `city`",
            "MAX(c.`zip`) `zip`",
            "MAX(c.`hospital_subtype`) `hospital_subtype`",
            "MAX(c.`fips_code`) `fips_code`",
            "MAX(c.`is_metro_micro`) `is_metro_micro`",
        ]
    )
    # basic query info
    group = "c.`hospital_pk`"
    order = "c.`hospital_pk` ASC"
    # build the filter
    # these are all fast because the table has indexes on each of these fields
    condition = "FALSE"
    params = dict()
    if state:
        condition = filter_strings("c.`state`", state, "state", params)
    elif ccn:
        condition = filter_strings("c.`ccn`", ccn, "ccn", params)
    elif city:
        condition = filter_strings("c.`city`", city, "city", params)
    elif zip:
        condition = filter_strings("c.`zip`", zip, "zip", params)
    elif fips_code:
        condition = filter_strings("c.`fips_code`", fips_code, "fips_code", params)

    # final query using specific issues
    query = f"SELECT {fields} FROM {table} WHERE ({condition}) GROUP BY {group} ORDER BY {order}"

    fields_string = [
        "hospital_pk",
        "state",
        "ccn",
        "hospital_name",
        "address",
        "city",
        "zip",
        "hospital_subtype",
        "fips_code",
    ]
    fields_int = ["is_metro_micro"]
    fields_float = []

    # send query
    return execute_query(query, params, fields_string, fields_int, fields_float)
