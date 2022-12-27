import pathlib
import logging
from typing import Dict, Callable

from flask import request, send_file, Response, send_from_directory, jsonify

from ._config import URL_PREFIX, VERSION, RATE_LIMIT
from ._db import metadata, engine
from ._common import app, set_compatibility_mode
from ._exceptions import MissingOrWrongSourceException
from .endpoints import endpoints
from .endpoints.admin import bp as admin_bp, enable_admin
from ._security import limiter, deduct_on_success, register_user_role
from ._config import UserRole

__all__ = ["app"]

endpoint_map: Dict[str, Callable[[], Response]] = {}

for endpoint in endpoints:
    endpoint_map[endpoint.bp.name] = endpoint.handle
    limiter.limit(RATE_LIMIT, deduct_when=deduct_on_success)(endpoint.bp)
    app.register_blueprint(endpoint.bp, url_prefix=f"{URL_PREFIX}/{endpoint.bp.name}")
    alias = getattr(endpoint, "alias", None)
    if alias:
        endpoint_map[alias] = endpoint.handle

with app.app_context():
    for role in UserRole:
        register_user_role(role.name)

if enable_admin():
    limiter.exempt(admin_bp)
    app.register_blueprint(admin_bp, url_prefix=f"{URL_PREFIX}/admin")


@app.route(f"{URL_PREFIX}/api.php", methods=["GET", "POST"])
@limiter.limit(RATE_LIMIT, deduct_when=deduct_on_success)
def handle_generic():
    # mark as compatibility mode
    set_compatibility_mode()
    endpoint = request.values.get("endpoint", request.values.get("source"))
    if not endpoint or endpoint not in endpoint_map:
        raise MissingOrWrongSourceException(endpoint_map.keys())
    return endpoint_map[endpoint]()


@app.route(f"{URL_PREFIX}")
@app.route(f"{URL_PREFIX}/")
@app.route(f"{URL_PREFIX}/index.html")
def send_index_file():
    return send_file(pathlib.Path(__file__).parent / "index.html")


@app.route(f"{URL_PREFIX}/version")
def send_version():
    return jsonify(dict(version=VERSION))


@app.route(f"{URL_PREFIX}/lib/<path:path>")
def send_lib_file(path: str):
    return send_from_directory(pathlib.Path(__file__).parent / "lib", path)


metadata.create_all(engine)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
else:
    # propagate gunicorn logging settings
    gunicorn_logger = logging.getLogger("gunicorn.error")
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)
    sqlalchemy_logger = logging.getLogger("sqlalchemy")
    sqlalchemy_logger.handlers = gunicorn_logger.handlers
    sqlalchemy_logger.setLevel(logging.ERROR)
    #sqlalchemy_logger.setLevel(gunicorn_logger.level)
