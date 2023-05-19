import pathlib
import logging
from typing import Dict, Callable

from flask import request, send_file, Response, send_from_directory, jsonify

from delphi.epidata.common.logger import get_structured_logger

from ._config import URL_PREFIX, VERSION
from ._common import app, set_compatibility_mode
from ._db import metadata, engine
from ._exceptions import MissingOrWrongSourceException
from .endpoints import endpoints
from .endpoints.admin import bp as admin_bp, enable_admin
from ._security import register_user_role
from ._limiter import limiter, apply_limit

__all__ = ["app"]

logger = get_structured_logger("webapp_main")

endpoint_map: Dict[str, Callable[[], Response]] = {}

for endpoint in endpoints:
    logger.info("registering endpoint", bp_name=endpoint.bp.name)
    apply_limit(endpoint.bp)
    app.register_blueprint(endpoint.bp, url_prefix=f"{URL_PREFIX}/{endpoint.bp.name}")

    endpoint_map[endpoint.bp.name] = endpoint.handle
    alias = getattr(endpoint, "alias", None)
    if alias:
        logger.info("endpoint has alias", bp_name=endpoint.bp.name, alias=alias)
        endpoint_map[alias] = endpoint.handle

if enable_admin():
    logger.info("admin endpoint enabled")
    limiter.exempt(admin_bp)
    app.register_blueprint(admin_bp, url_prefix=f"{URL_PREFIX}/admin")


@app.route(f"{URL_PREFIX}/api.php", methods=["GET", "POST"])
@apply_limit
def handle_generic():
    # mark as compatibility mode
    set_compatibility_mode()
    endpoint = request.values.get("endpoint", request.values.get("source"))
    if not endpoint or endpoint not in endpoint_map:
        raise MissingOrWrongSourceException(endpoint_map.keys())
    return endpoint_map[endpoint]()


# @app.route(f"{URL_PREFIX}") # TODO: make sure we dont need this line
@app.route(f"{URL_PREFIX}/")
@app.route(f"{URL_PREFIX}/index.html")
def send_index_file():
    return send_file(pathlib.Path(__file__).parent / "index.html")


# TODO: remove
from ._exceptions import DatabaseErrorException
@app.route(f"{URL_PREFIX}/fake_db_error")
def cause_fake_db_error():
    raise DatabaseErrorException("fake_db_error")


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
