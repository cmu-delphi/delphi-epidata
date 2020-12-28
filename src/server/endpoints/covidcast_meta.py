from flask import jsonify, request, Blueprint

from sqlalchemy import select
from .._common import app, db

bp = Blueprint("covidcast_meta", __name__)


@bp.route("/", methods=("GET", "POST"))
def handle():
    # complain if the cache is more than 75 minutes old
    max_age = 75 * 60

    return jsonify({"test": request.values.get("test", "No")})
