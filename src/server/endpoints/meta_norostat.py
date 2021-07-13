from flask import Blueprint

from .._printer import print_non_standard
from .._query import parse_result
from .._security import UserRole

# first argument is the endpoint name
bp = Blueprint("meta_norostat", __name__)
required_role = UserRole.norostat
alias = None


@bp.route("/", methods=("GET", "POST"))
def handle():
    # build query
    query = "SELECT DISTINCT `release_date` FROM `norostat_raw_datatable_version_list`"
    releases = parse_result(query, {}, ["release_date"])

    query = "SELECT DISTINCT `location` FROM `norostat_raw_datatable_location_pool`"
    locations = parse_result(query, {}, ["location"])

    data = {"releases": releases, "locations": locations}
    return print_non_standard(data)
