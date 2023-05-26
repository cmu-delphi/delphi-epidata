from typing import cast
import time

from flask import Flask, g, request
from sqlalchemy import event
from sqlalchemy.engine import Connection
from werkzeug.exceptions import Unauthorized
from werkzeug.local import LocalProxy

from delphi.epidata.common.logger import get_structured_logger
from ._config import SECRET, REVERSE_PROXIED
from ._db import engine
from ._exceptions import DatabaseErrorException, EpiDataException
from ._security import current_user, _is_public_route, resolve_auth_token, show_no_api_key_warning, update_key_last_time_used, ERROR_MSG_INVALID_KEY


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
    if REVERSE_PROXIED:
        # NOTE: ONLY trust these headers if reverse proxied!!!
        if "X-Forwarded-For" in req.headers:
            return req.headers["X-Forwarded-For"].split(",")[
                0
            ]  # take the first (or only) address from the comma-sep list
        if "X-Real-Ip" in req.headers:
            return req.headers["X-Real-Ip"]
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

@event.listens_for(engine, "before_cursor_execute")
def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    context._query_start_time = time.time()


@event.listens_for(engine, "after_cursor_execute")
def after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    # this timing info may be suspect, at least in terms of dbms cpu time...
    # it is likely that it includes that time as well as any overhead that
    # comes from throttling or flow control on the streamed data, as well as
    # any row transform/processing time
    total_time = time.time() - context._query_start_time

    # Convert to milliseconds
    total_time *= 1000
    get_structured_logger("server_api").info(
        "Executed SQL", statement=statement, params=parameters, elapsed_time_ms=total_time
    )


@app.before_request
def before_request_execute():
    # Set timer for statement
    g._request_start_time = time.time()

    user = current_user
    api_key = resolve_auth_token()

    # TODO: replace this next call with: log_info_with_request("Received API request")
    get_structured_logger("server_api").info(
        "Received API request",
        method=request.method,
        url=request.url,
        form_args=request.form,
        req_length=request.content_length,
        remote_addr=request.remote_addr,
        real_remote_addr=get_real_ip_addr(request),
        user_agent=request.user_agent.string,
        api_key=api_key,
        user_id=(user and user.id)
    )

    if not show_no_api_key_warning():
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

    api_key = resolve_auth_token()

    update_key_last_time_used(current_user)

    # TODO: replace this next call with: log_info_with_request_and_response("Served API request", response, elapsed_time_ms=total_time)
    get_structured_logger("server_api").info(
        "Served API request",
        method=request.method,
        url=request.url,
        form_args=request.form,
        req_length=request.content_length,
        remote_addr=request.remote_addr,
        real_remote_addr=get_real_ip_addr(request),
        user_agent=request.user_agent.string,
        api_key=api_key,
        values=request.values.to_dict(flat=False),
        blueprint=request.blueprint,
        endpoint=request.endpoint,
        response_status=response.status,
        content_length=response.calculate_content_length(),
        elapsed_time_ms=total_time,
    )
    return response


@app.teardown_appcontext
def teardown_db(exception=None):
    # drop reference to "user" (if it exists)
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
