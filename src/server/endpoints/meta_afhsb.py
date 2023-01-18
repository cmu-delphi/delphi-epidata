from flask import Blueprint, request

from .._config import AUTH
from .._printer import print_non_standard
from .._query import parse_result
from .._validate import check_auth_token

# first argument is the endpoint name
bp = Blueprint("meta_afhsb", __name__)
alias = None


@bp.route("/", methods=("GET", "POST"))
def handle():
    check_auth_token(request, AUTH["afhsb"])

    # build query
    table1 = "afhsb_00to13_state"
    table2 = "afhsb_13to17_state"

    string_keys = ["state", "country"]
    int_keys = ["flu_severity"]
    data = dict()

    for key in string_keys:
        query = f"SELECT DISTINCT `{key}` FROM (select `{key}` from `{table1}` union select `{key}` from `{table2}`) t"
        data[key] = parse_result(query, {}, [key])
    for key in int_keys:
        query = f"SELECT DISTINCT `{key}` FROM (select `{key}` from `{table1}` union select `{key}` from `{table2}`) t"
        data[key] = parse_result(query, {}, [], [key])

    return print_non_standard(request, data)
