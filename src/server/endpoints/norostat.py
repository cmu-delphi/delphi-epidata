from flask import Blueprint, request

from .._query import execute_query, filter_integers, filter_strings
from .._validate import extract_integers, require_all
from .._security import require_role
from .._config import UserRole

# first argument is the endpoint name
bp = Blueprint("norostat", __name__)
alias = None


@bp.route("/", methods=("GET", "POST"))
@require_role(UserRole.norostat)
def handle():
    require_all("location", "epiweeks")

    location = request.values["location"]
    epiweeks = extract_integers("epiweeks")

    # build query
    # build the filter
    params = dict()
    # build the location filter
    condition_location = filter_strings(
        "`norostat_raw_datatable_location_pool`.`location`", [location], "loc", params
    )
    condition_epiweek = filter_integers(
        "`latest`.`epiweek`", epiweeks, "epiweek", params
    )
    # the query
    query = f"""
        SELECT `latest`.`release_date`, `latest`.`epiweek`, `latest`.`new_value` AS `value`
        FROM `norostat_point_diffs` AS `latest`
        LEFT JOIN `norostat_raw_datatable_location_pool` USING (`location_id`)
        LEFT JOIN (
        SELECT * FROM `norostat_point_diffs`
        ) `later`
        ON `latest`.`location_id` = `later`.`location_id` AND
        `latest`.`epiweek` = `later`.`epiweek` AND
        (`latest`.`release_date`, `latest`.`parse_time`) <
            (`later`.`release_date`, `later`.`parse_time`) AND
        `later`.`new_value` IS NOT NULL
        WHERE ({condition_location}) AND
            ({condition_epiweek}) AND
            `later`.`parse_time` IS NULL AND
            `latest`.`new_value` IS NOT NULL
    """

    fields_string = ["release_date"]
    fields_int = ["epiweek", "value"]
    fields_float = []

    # send query
    return execute_query(query, params, fields_string, fields_int, fields_float)
