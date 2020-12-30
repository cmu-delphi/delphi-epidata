import pathlib
from typing import Dict, Callable

from flask import request, send_file, Response

from ._common import app
from ._exceptions import MissingOrWrongSourceException
from .endpoints import endpoints

__all__ = ["app"]


endpoint_map: Dict[str, Callable[[], Response]] = {}

for endpoint in endpoints:
    endpoint_map[endpoint.bp.name] = endpoint.handle
    app.register_blueprint(endpoint.bp, url_prefix=f"/{endpoint.bp.name}")

    alias = getattr(endpoint, "alias", None)
    if alias:
        endpoint_map[alias] = endpoint.handle


@app.route("/api.php", methods=["GET", "POST"])
def handle_generic():
    endpoint = request.values.get("endpoint", request.values.get("source"))
    if not endpoint or endpoint not in endpoint_map:
        raise MissingOrWrongSourceException()
    return endpoint_map[endpoint]()


@app.route("/")
@app.route("/index.html")
def send_index_file():
    return send_file(pathlib.Path(__file__).parent / "index.html")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
