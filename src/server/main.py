import os
import pathlib
import logging
import sentry_sdk
import socket
import json
from typing import Dict, Callable

from flask import request, send_file, Response, send_from_directory, jsonify, make_response

from delphi.epidata.common.logger import get_structured_logger

from ._config import URL_PREFIX, VERSION
from ._common import app, db, set_compatibility_mode, log_info_with_request
from .endpoints.admin import _require_admin
from ._exceptions import MissingOrWrongSourceException
from .endpoints import endpoints
from .endpoints.admin import *
from ._limiter import apply_limit

SENTRY_DSN = os.environ.get('SENTRY_DSN')
if SENTRY_DSN:
    sentry_sdk.init(
        dsn = SENTRY_DSN,
        environment = os.environ.get('SENTRY_ENVIRONMENT', 'development'),
        profiles_sample_rate = float(os.environ.get('SENTRY_PROFILES_SAMPLE_RATE', 1.0)),
        traces_sample_rate = float(os.environ.get('SENTRY_TRACES_SAMPLE_RATE', 1.0)),
        attach_stacktrace = os.environ.get('SENTRY_ATTACH_STACKTRACE', 'False').lower() in ('true', '1', 't'),
        debug = os.environ.get('SENTRY_DEBUG', 'False').lower() in ('true', '1', 't')
    )


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

@app.route(f"{URL_PREFIX}/api.php", methods=["GET", "POST"])
@apply_limit
def handle_generic():
    # mark as compatibility mode
    set_compatibility_mode()
    endpoint = request.values.get("endpoint", request.values.get("source"))
    if not endpoint or endpoint not in endpoint_map:
        raise MissingOrWrongSourceException(endpoint_map.keys())
    return endpoint_map[endpoint]()


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


@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory("/app/delphi/epidata/server/static", path)


@app.route("/diagnostics", methods=["GET", "PUT", "POST", "DELETE"])
def diags():
    # allows us to get useful diagnostic information written into server logs,
    # such as a full current "X-Forwarded-For" path as inserted into headers by intermediate proxies...
    # (but only when initiated purposefully by us to keep junk out of the logs)
    _require_admin()

    try:
        serving_host = socket.gethostbyname_ex(socket.gethostname())
    except Exception as e:
        serving_host = e

    try:
        db_host = db.execute('SELECT @@hostname AS hn').fetchone()['hn']
    except Exception as e:
        db_host = e

    log_info_with_request("diagnostics", headers=request.headers, serving_host=serving_host, database_host=db_host)

    response_data = {
        'request_path': request.headers.get('X-Forwarded-For', 'idfk'),
        'serving_host': serving_host,
        'database_host': db_host,
    }
    return make_response(json.dumps(response_data), 200, {'content-type': 'text/plain'})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
else:
    # propagate gunicorn logging settings
    gunicorn_logger = logging.getLogger("gunicorn.error")
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)
    sqlalchemy_logger = logging.getLogger("sqlalchemy")
    sqlalchemy_logger.handlers = gunicorn_logger.handlers
    sqlalchemy_logger.setLevel(logging.WARN)
    # WAS: sqlalchemy_logger.setLevel(gunicorn_logger.level)
