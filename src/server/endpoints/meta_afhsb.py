from flask import request, Blueprint

from sqlalchemy import text
from .._common import app, db
from .._config import AUTH
from .._validate import require_all, extract_strings, extract_integers, check_auth_token
from .._query import filter_strings, execute_query
from .._printer import print_non_standard

# first argument is the endpoint name
bp = Blueprint("meta_afhsb", __name__)
alias = None


@bp.route("/", methods=("GET", "POST"))
def handle():
    check_auth_token(AUTH["afhsb"])

    # build query
    table1 = "afhsb_00to13_state"
    table2 = "afhsb_13to17_state"

    string_keys = ["state", "country"]
    int_keys = ["flu_severity"]
    data = dict()

    for key in string_keys:
        query = f"SELECT DISTINCT `{key}` FROM (select `{key}` from `{table1}` union select `{key}` from `{table2}`) t"
        r = db.execute(text(query))
        data[key] = [{key: row.get(key)} for row in r]
    for key in int_keys:
        query = f"SELECT DISTINCT `{key}` FROM (select `{key}` from `{table1}` union select `{key}` from `{table2}`) t"
        r = db.execute(text(query))
        data[key] = [{key: (int(row[key]) if key in row else None)} for row in r]

    return print_non_standard(data)
