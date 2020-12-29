from flask import request, Blueprint

from sqlalchemy import text
from .._common import app, db
from .._config import AUTH
from .._exceptions import UnAuthenticatedException
from .._validate import require_all, extract_strings, extract_integers
from .._query import filter_strings, execute_query
from .._printer import print_non_standard

# first argument is the endpoint name
bp = Blueprint("meta_norostat", __name__)
alias = None


@bp.route("/", methods=("GET", "POST"))
def handle():
    require_all("auth")
    if request.values["auth"] != AUTH["norostat"]:
        raise UnAuthenticatedException()

    # build query
    query = "SELECT DISTINCT `release_date` FROM `norostat_raw_datatable_version_list`"
    releases = [
        {"release_date": row.get("release_date")} for row in db.execute(text(query))
    ]

    query = "SELECT DISTINCT `location` FROM `norostat_raw_datatable_location_pool`"
    locations = [{"location": row.get("location")} for row in db.execute(text(query))]

    data = {"releases": releases, "locations": locations}
    return print_non_standard(data)
