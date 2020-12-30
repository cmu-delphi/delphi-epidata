from flask import request, Blueprint

from sqlalchemy import text
from .._common import app, db
from .._config import AUTH
from .._exceptions import UnAuthenticatedException
from .._validate import require_all, extract_strings, extract_integers, filter_fields
from .._query import filter_strings, execute_query, parse_result
from .._printer import create_printer

# first argument is the endpoint name
bp = Blueprint("fluview_meta", __name__)
alias = None


def meta_fluview():
    query = "SELECT max(`release_date`) `latest_update`, max(`issue`) `latest_issue`, count(1) `table_rows` FROM `fluview`"
    fields_string = ["latest_update"]
    fields_int = ["latest_issue", "table_rows"]
    return parse_result(query, {}, fields_string, fields_int, None)


@bp.route("/", methods=("GET", "POST"))
def handle():
    # query and return metadata

    def gen():
        for row in meta_fluview():
            yield row

    return create_printer()(filter_fields(gen()))
