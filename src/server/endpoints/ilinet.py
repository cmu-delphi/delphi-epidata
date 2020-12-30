from flask import jsonify, request, Blueprint

from sqlalchemy import select
from .._common import app, db
from .._config import AUTH
from .._validate import require_all, extract_strings, extract_integers
from .._query import filter_strings, execute_query, filter_integers
from .._exceptions import EpiDataException

# first argument is the endpoint name
bp = Blueprint("ilinet", __name__)
alias = "stateili"


@bp.route("/", methods=("GET", "POST"))
def handle():
    raise EpiDataException("use fluview instead")
