from flask import jsonify, request, Blueprint

from sqlalchemy import select
from .._common import app, db
from .._config import AUTH
from .._validate import require_all, extract_strings, extract_ints

bp = Blueprint("fluview", __name__)


@bp.route("/", methods=("GET", "POST"))
def handle():
    require_all("epiweeks", "regions")

    epiweeks = extract_ints("epiweeks")
    regions = extract_strings("regions")
    issues = extract_ints("isues")
    lag = int(request.values["lag"]) if "lag" in request.values else None
    authorized = request.values.get("auth") == AUTH["fluview"]

    table = "fluview fv"
    fields = "fv.release_date, fv.issue, fv.epiweek, fv.region, fv.lag"

    return jsonify({"test": request.values.get("test", "No")})
