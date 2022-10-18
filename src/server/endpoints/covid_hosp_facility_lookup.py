from flask import Blueprint

from .._query import execute_query, QueryBuilder
from .._validate import extract_strings, require_any

# first argument is the endpoint name
bp = Blueprint("covid_hosp_facility_lookup", __name__)
required_role = None


@bp.route("/", methods=("GET", "POST"))
def handle():
    require_any("state", "ccn", "city", "zip", "fips_code")
    state = extract_strings("state")
    ccn = extract_strings("ccn")
    city = extract_strings("city")
    zip = extract_strings("zip")
    fips_code = extract_strings("fips_code")

    # build query
    q = QueryBuilder("covid_hosp_facility", "c")
    q.fields = ", ".join(
        [
            f"{q.alias}.hospital_pk",
            f"MAX({q.alias}.state) state",
            f"MAX({q.alias}.ccn) ccn",
            f"MAX({q.alias}.hospital_name) hospital_name",
            f"MAX({q.alias}.address) address",
            f"MAX({q.alias}.city) city",
            f"MAX({q.alias}.zip) zip",
            f"MAX({q.alias}.hospital_subtype) hospital_subtype",
            f"MAX({q.alias}.fips_code) fips_code",
            f"MAX({q.alias}.is_metro_micro) is_metro_micro",
        ]
    )
    # basic query info
    q.group_by = f"{q.alias}.hospital_pk"
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
