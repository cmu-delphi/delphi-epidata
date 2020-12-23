from typing import List, Optional
import json
import datetime
from enum import Enum
from flask import jsonify, request

from ._common import app


@app.route("/covidcast_meta", methods=["GET", "POST"])
def covidcast_meta():
    return jsonify({"test": request.values.get("test", "No")})
