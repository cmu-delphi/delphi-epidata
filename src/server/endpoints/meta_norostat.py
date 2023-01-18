from flask import Blueprint, request

from .._config import AUTH
from .._printer import print_non_standard
from .._query import parse_result
from .._validate import check_auth_token

# first argument is the endpoint name
bp = Blueprint("meta_norostat", __name__)
alias = None


@bp.route("/", methods=("GET", "POST"))
def handle():
    check_auth_token(request, AUTH["norostat"])

    # build query
    query = "SELECT DISTINCT `release_date` FROM `norostat_raw_datatable_version_list`"
    releases = parse_result(query, {}, ["release_date"])

    query = "SELECT DISTINCT `location` FROM `norostat_raw_datatable_location_pool`"
    locations = parse_result(query, {}, ["location"])

    data = {"releases": releases, "locations": locations}
    return print_non_standard(data)
