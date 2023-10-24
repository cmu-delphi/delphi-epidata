from flask import Blueprint
from .._exceptions import EpiDataException

# first argument is the endpoint name
bp = Blueprint("covidcast_nowcast", __name__)
alias = None


@bp.route("/", methods=("GET", "POST"))
def handle():
    """[DEPRECATED] Fetch Delphi's COVID-19 Nowcast sensors"""
    raise EpiDataException("This endpoint is deprecated.")
