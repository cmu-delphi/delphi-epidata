from flask import Blueprint

from .._query import execute_query, QueryBuilder
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
    q = QueryBuilder("covid_hosp_facility_key", "c")
    q.fields = ", ".join(
        [ # NOTE: fields `geocoded_hospital_address` and `hhs_ids` are available but not being provided by this endpoint.
            f"{q.alias}.hospital_pk",
            f"{q.alias}.state",
            f"{q.alias}.ccn",
            f"{q.alias}.hospital_name",
            f"{q.alias}.address",
            f"{q.alias}.city",
            f"{q.alias}.zip",
            f"{q.alias}.hospital_subtype",
            f"{q.alias}.fips_code",
            f"{q.alias}.is_metro_micro",
        ]
    )
    # basic query info
    q.set_order("hospital_pk")
    # build the filter
    # these are all fast because the table has indexes on each of these fields
    if state:
        q.where_strings('state', state)
    elif ccn:
        q.where_strings('ccn', ccn)
    elif city:
        q.where_strings('city', city)
    elif zip:
        q.where_strings("zip", zip)
    elif fips_code:
        q.where_strings("fips_code", fips_code)
    else:
        q.conditions.append('FALSE')

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
    return execute_query(str(q), q.params, fields_string, fields_int, fields_float)
