import pathlib
import logging
from typing import Dict, Callable

from flask import request, send_file, Response

from ._config import URL_PREFIX
from ._common import app
from ._exceptions import MissingOrWrongSourceException
from .endpoints import endpoints

__all__ = ["app"]


endpoint_map: Dict[str, Callable[[], Response]] = {}

for endpoint in endpoints:
    endpoint_map[endpoint.bp.name] = endpoint.handle
    app.register_blueprint(endpoint.bp, url_prefix=f"{URL_PREFIX}/{endpoint.bp.name}")

    alias = getattr(endpoint, "alias", None)
    if alias:
        endpoint_map[alias] = endpoint.handle


@app.route(f"{URL_PREFIX}/api.php", methods=["GET", "POST"])
def handle_generic():
    endpoint = request.values.get("endpoint", request.values.get("source"))
    if not endpoint or endpoint not in endpoint_map:
        raise MissingOrWrongSourceException(endpoint_map.keys())
    return endpoint_map[endpoint]()


@app.route(f"{URL_PREFIX}")
@app.route(f"{URL_PREFIX}/")
@app.route(f"{URL_PREFIX}/index.html")
def send_index_file():
    return send_file(pathlib.Path(__file__).parent / "index.html")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
else:
    # propagate gunicorn logging settings
    gunicorn_logger = logging.getLogger("gunicorn.error")
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)
    sqlalchemy_logger = logging.getLogger("sqlalchemy")
    sqlalchemy_logger.handlers = gunicorn_logger.handlers
    sqlalchemy_logger.setLevel(gunicorn_logger.level)
