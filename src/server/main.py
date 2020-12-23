from ._common import app
from flask import send_file, request, abort
import pathlib

from .covidcast_meta import covidcast_meta

__all__ = ["app"]

endpoints = {"covidcast_meta": covidcast_meta}


@app.route("/api.php", methods=["GET", "POST"])
def handle_generic():
    endpoint = request.values.get("endpoint", request.values.get("source"))
    if not endpoint or endpoint not in endpoints:
        abort(401)
    return endpoints[endpoint]()


@app.route("/")
@app.route("/index.html")
def send_index_file():
    return send_file(pathlib.Path(__file__).parent / "index.html")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
