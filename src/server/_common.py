from typing import cast
import time

from flask import Flask, g, request
from sqlalchemy import event
from sqlalchemy.engine import Connection, Engine
from werkzeug.exceptions import Unauthorized
from werkzeug.local import LocalProxy

from delphi_utils import get_structured_logger
from ._config import SECRET, REVERSE_PROXY_DEPTH
from ._db import engine
from ._exceptions import DatabaseErrorException, EpiDataException
from ._security import current_user, _is_public_route, resolve_auth_token, update_key_last_time_used, ERROR_MSG_INVALID_KEY


app = Flask("EpiData", static_url_path="")
app.config["SECRET"] = SECRET


def _get_db() -> Connection:
    if "db" not in g:
        conn = engine.connect()
        g.db = conn
    return g.db

"""
access to the SQL Alchemy connection for this request
"""
db: Connection = cast(Connection, LocalProxy(_get_db))


def get_real_ip_addr(req):  # `req` should be a Flask.request object
    if REVERSE_PROXY_DEPTH:
        # we only expect/trust (up to) "REVERSE_PROXY_DEPTH" number of proxies between this server and the outside world.
        # a REVERSE_PROXY_DEPTH of 0 means not proxied, i.e. server is globally directly reachable.
        # a negative proxy depth is a special case to trust the whole chain -- not generally recommended unless the
        # most-external proxy is configured to disregard "X-Forwarded-For" from outside.
        # really, ONLY trust the following headers if reverse proxied!!!
        if "X-Forwarded-For" in req.headers:
            full_proxy_chain = req.headers["X-Forwarded-For"].split(",")
            # eliminate any extra addresses at the front of this list, as they could be spoofed.
            if REVERSE_PROXY_DEPTH > 0:
                depth = REVERSE_PROXY_DEPTH
            else:
                # special case for -1/negative: setting `depth` to 0 will not strip any items from the chain
                depth = 0
            trusted_proxy_chain = full_proxy_chain[-depth:]
            # accept the first (or only) address in the remaining trusted part of the chain as the actual remote address
            return trusted_proxy_chain[0].strip()

        # fall back to "X-Real-Ip" if "X-Forwarded-For" isnt present
        if "X-Real-Ip" in req.headers:
            return req.headers["X-Real-Ip"]

    # if we are not proxied (or we are proxied but the headers werent present and we fell through to here), just use the remote ip addr as the true client address
    return req.remote_addr


def log_info_with_request(message, **kwargs):
    # TODO: make log level an option and check for key conflicts in kwargs
    get_structured_logger("server_api").info(
        message,
        method=request.method,
        url=request.url,
        form_args=request.form,
        req_length=request.content_length,
        remote_addr=request.remote_addr,
        real_remote_addr=get_real_ip_addr(request),
        user_agent=request.user_agent.string,
        referrer=request.referrer or request.origin,
        api_key=resolve_auth_token(),
        user_id=(current_user and current_user.id),
        **kwargs
    )

def log_info_with_request_and_response(message, response, **kwargs):
    # TODO: make log level an option and check for key conflicts in kwargs
    log_info_with_request(
        message,
        values=request.values.to_dict(flat=False),
        blueprint=request.blueprint,
        endpoint=request.endpoint,
        response_status=response.status,
        content_length=response.calculate_content_length(),
        **kwargs
    )

@event.listens_for(Engine, "before_cursor_execute")
def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    context._query_start_time = time.time()


@event.listens_for(Engine, "after_cursor_execute")
def after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    # this timing info may be suspect, at least in terms of dbms cpu time...
    # it is likely that it includes that time as well as any overhead that
    # comes from throttling or flow control on the streamed data, as well as
    # any row transform/processing time
    total_time = time.time() - context._query_start_time

    # Convert to milliseconds
    total_time *= 1000
    get_structured_logger("server_api").info(
        "Executed SQL", statement=statement, params=parameters, elapsed_time_ms=total_time,
        engine_id=conn.get_execution_options().get('engine_id')
    )


@app.before_request
def before_request_execute():
    # Set timer for statement
    g._request_start_time = time.time()

    user = current_user
    api_key = resolve_auth_token()

    log_info_with_request("Received API request")

    if not _is_public_route() and api_key and not user:
        # if this is a privleged endpoint, and an api key was given but it does not look up to a user, raise exception:
        get_structured_logger("server_api").info("bad api key used", api_key=api_key)
        raise Unauthorized(ERROR_MSG_INVALID_KEY)

    if request.path.startswith("/lib"):
        # files served from 'lib' directory don't need the database, so we can exit this early...
        return
    # try to get the db
    try:
        _get_db()
    except Exception as e:
        get_structured_logger("server_error").error("database connection error", exception=e)
        raise DatabaseErrorException()


@app.after_request
def after_request_execute(response):
    total_time = time.time() - g._request_start_time
    # Convert to milliseconds
    total_time *= 1000

    update_key_last_time_used(current_user)

    log_info_with_request_and_response("Served API request", response, elapsed_time_ms=total_time)

    return response


@app.teardown_appcontext
def teardown_db(exception=None):
    # drop reference to "user" (if it exists)
    if "user" in g:
        g.pop("user")

    # close the db connection
    db = g.pop("db", None)

    if db is not None:
        db.close()


@app.errorhandler(EpiDataException)
def handle_exception(e):
    # Log error and pass through; EpiDataExceptions are HTTPExceptions which are valid WSGI responses (see https://werkzeug.palletsprojects.com/en/2.2.x/exceptions/ )
    if isinstance(e, DatabaseErrorException):
        get_structured_logger("server_error").error("Received DatabaseErrorException", exception=str(e), exc_info=True)
    else:
        get_structured_logger("server_error").warn("Encountered user-side error", exception=str(e))
    return e


def is_compatibility_mode() -> bool:
    """
    checks whether this request is in compatibility mode
    """
    return "compatibility" in g and g.compatibility


def set_compatibility_mode():
    """
    sets the compatibility mode for this request
    """
    g.compatibility = True
