from flask import Blueprint

from .._exceptions import EpiDataException

# first argument is the endpoint name
bp = Blueprint("ilinet", __name__)
alias = "stateili"


@bp.route("/", methods=("GET", "POST"))
def handle():
    raise EpiDataException("use fluview instead")
