from flask import Blueprint, request
from flask.json import loads

from .._printer import print_non_standard
from .._query import parse_result
from .._validate import require_all

# first argument is the endpoint name
bp = Blueprint("delphi", __name__)
alias = None


@bp.route("/", methods=("GET", "POST"))
def handle():
    require_all(request, "system", "epiweek")
    system = request.values["system"]
    epiweek = int(request.values["epiweek"])

    # build query
    query = "SELECT `system`, `epiweek`, `json` FROM `forecasts` WHERE `system` = :system AND `epiweek` = :epiweek LIMIT 1"
    params = dict(system=system, epiweek=epiweek)

    fields_string = ["system", "json"]
    fields_int = ["epiweek"]
    fields_float = []

    rows = parse_result(query, params, fields_string, fields_int, fields_float)
    for row in rows:
        row["forecast"] = loads(row["json"])
        del row["json"]
    # send query
    return print_non_standard(request, rows)
