from typing import Dict, List

from flask import Blueprint

from .._config import AUTH
from .._query import execute_queries, filter_integers, filter_strings
from .._validate import check_auth_token, extract_integers, extract_strings, require_all

# first argument is the endpoint name
bp = Blueprint("afhsb", __name__)
alias = None


def _split_locations(locations: List[str]):
    # split locations into national/regional/state
    location_dict: Dict[str, List[str]] = {
        "hhs": [],
        "cen": [],
        "state": [],
        "country": [],
    }
    for location in locations:
        location = location.lower()
        if location[0:3] == "hhs":
            location_dict["hhs"].append(location)
        elif location[0:3] == "cen":
            location_dict["cen"].append(location)
        elif len(location) == 3:
            location_dict["country"].append(location)
        elif len(location) == 2:
            location_dict["state"].append(location)
    return location_dict


def _split_flu_types(flu_types: List[str]):
    # split flu types into disjoint/subset
    disjoint_flus = []
    subset_flus = []
    for flu_type in flu_types:
        if flu_type in ["flu1", "flu2-flu1", "flu3-flu2", "ili-flu3"]:
            disjoint_flus.append(flu_type)
        elif flu_type in ["flu2", "flu3", "ili"]:
            subset_flus.append(flu_type)
    return disjoint_flus, subset_flus


FLU_MAPPING = {
    "flu2": ["flu1", "flu2-flu1"],
    "flu3": ["flu1", "flu2-flu1", "flu3-flu2"],
    "ili": ["flu1", "flu2-flu1", "flu3-flu2", "ili-flu3"],
}


@bp.route("/", methods=("GET", "POST"))
def handle():
    check_auth_token(AUTH["afhsb"])
    require_all("locations", "epiweeks", "flu_types")

    locations = extract_strings("locations")
    epiweeks = extract_integers("epiweeks")
    flu_types = extract_strings("flu_types")

    disjoint_flus, subset_flus = _split_flu_types(flu_types)
    location_dict = _split_locations(locations)

    # build query

    queries = []
    for location_type, loc in location_dict.items():
        if not loc:
            continue
        table = (
            "afhsb_00to13_region"
            if location_type in ["hhs", "cen"]
            else "afhsb_00to13_state"
        )
        fields = (
            f"`epiweek`, `{location_type}` `location`, sum(`visit_sum`) `visit_sum`"
        )
        group = "`epiweek`, `location`"
        order = "`epiweek` ASC, `location` ASC"
        # build the filter
        params = dict()
        # build the epiweek filter
        condition_epiweek = filter_integers("nd.`epiweek`", epiweeks, "epiweek", params)
        condition_location = filter_strings(location_type, locations, "loc", params)

        for subset_flu in subset_flus:
            flu_params = params.copy()
            condition_flu = filter_strings(
                "`flu_type`", FLU_MAPPING[subset_flu], "flu_type", flu_params
            )
            query = f"""SELECT {fields}, '{subset_flu}' `flu_type` FROM {table}
                        WHERE ({condition_epiweek}) AND ({condition_location}) AND ({condition_flu})
                        GROUP BY {group} ORDER BY {order}"""
            queries.append((query, flu_params))
        # disjoint flu types: flu1, flu2-flu1, flu3-flu2, ili-flu3
        if disjoint_flus:
            flu_params = params.copy()
            condition_flu = filter_strings(
                "`flu_type`", disjoint_flus, "flu_type", flu_params
            )
            query = f"""SELECT {fields}, `flu_type` FROM {table}
                        WHERE ({condition_epiweek}) AND ({condition_location}) AND ({condition_flu})
                        GROUP BY {group},`flu_type` ORDER BY {order},`flu_type`"""
            queries.append((query, flu_params))

    fields_string = ["location", "flu_type"]
    fields_int = ["epiweek", "visit_sum"]
    fields_float = []

    # send query
    return execute_queries(queries, fields_string, fields_int, fields_float)
