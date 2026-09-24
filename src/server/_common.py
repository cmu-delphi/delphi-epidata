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


def _resolve_client_ip(remote_addr, x_forwarded_for, x_real_ip, depth):
    """Resolve the real client IP address from proxy headers.

    Only the rightmost ``depth`` entries of the ``X-Forwarded-For`` chain were
    appended by trusted proxies; everything to their left is client-controlled
    and must not be trusted as an identity -- doing so would let an anonymous
    client rotate a fresh rate-limit key per request and poison ``real_remote_addr``
    logs. When the chain is shorter than the declared depth (over-declared depth,
    or a client reaching the server directly), none of the chain is trustworthy,
    so the actual connecting peer address is used instead.

    A negative ``depth`` is the documented special case of trusting the whole
    chain, and is only safe when the outermost proxy strips client-supplied
    ``X-Forwarded-For`` headers. ``X-Real-Ip`` is only honored when the server is
    actually behind proxies (it is set -- and overwritten -- by the proxy itself).
    """
    if depth and x_forwarded_for:
        chain = [part.strip() for part in x_forwarded_for.split(",") if part.strip()]
        if chain:
            if depth > 0:
                if len(chain) >= depth:
                    # The leftmost entry of the trusted suffix is the client address
                    # as seen by the outermost trusted proxy.
                    return chain[-depth]
                # Over-declared depth (or a direct connection): none of the chain
                # is trustworthy, so fall back to the actual connecting peer
                # instead of trusting client-controlled entries.
                return remote_addr
            # Negative depth: trust the whole chain (see caveat above).
            return chain[0]
        # A blank X-Forwarded-For header carries no information; treat it as absent.
    if depth and x_real_ip:
        return x_real_ip
    return remote_addr


def get_real_ip_addr(req):  # `req` should be a Flask.request object
    # we only expect/trust (up to) "REVERSE_PROXY_DEPTH" number of proxies between this server and the outside world.
    # a REVERSE_PROXY_DEPTH of 0 means not proxied, i.e. server is globally directly reachable.
    # a negative proxy depth is a special case to trust the whole chain -- not generally recommended unless the
    # most-external proxy is configured to disregard "X-Forwarded-For" from outside.
    # really, ONLY trust the following headers if reverse proxied!!!
    return _resolve_client_ip(
        req.remote_addr,
        req.headers.get("X-Forwarded-For"),
        req.headers.get("X-Real-Ip"),
        REVERSE_PROXY_DEPTH,
    )


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
