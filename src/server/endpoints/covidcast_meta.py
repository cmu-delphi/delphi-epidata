from flask import jsonify, request, Blueprint

from .._common import app, db

bp = Blueprint("covidcast_meta", __name__, url_prefix="/covidcast_meta")


@bp.route("/", methods=("GET", "POST"))
def handle():
    return jsonify({"test": request.values.get("test", "No")})
