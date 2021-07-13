from flask import Blueprint

from .._printer import create_printer
from .._query import filter_fields, parse_result

# first argument is the endpoint name
bp = Blueprint("fluview_meta", __name__)
required_role = None
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
