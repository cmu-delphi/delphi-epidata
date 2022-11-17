from typing import cast
import time

from flask import Flask, g, request
from sqlalchemy import event
from sqlalchemy.engine import Connection
from werkzeug.local import LocalProxy
from werkzeug.exceptions import HTTPException

from .utils.logger import get_structured_logger
from ._config import SECRET
from ._db import engine
from ._exceptions import DatabaseErrorException, ValidationFailedException

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
    get_structured_logger('server_api').info("Executed SQL", statement=statement, params=parameters, elapsed_time_ms=total_time)


@app.before_request
def before_request_execute():
    # Set timer for statement
    g._request_start_time = time.time()

    # Log statement
    get_structured_logger('server_api').info("Received API request", method=request.method, headers=request.headers, path=request.full_path, args=request.args, user_agent=request.user_agent)

    if request.path.startswith('/lib'):
        return
    # try to get the db
    try:
        _get_db()
    except Exception as e:
        get_structured_logger('server_error').error('database connection error', exception=e)
        raise DatabaseErrorException()


@app.after_request
def after_request_execute(response):
    total_time = time.time() - g._request_start_time
    # Convert to milliseconds
    total_time *= 1000
    get_structured_logger('server_api').info('Served API request', method=request.method, headers=request.headers, path=request.full_path, args=request.args, user_agent=request.user_agent, response_status=response.status, response_length=response.content_length, elapsed_time_ms=total_time)
    return response


@app.teardown_appcontext
def teardown_db(exception=None):
    # close the db connection
    db = g.pop("db", None)

    if db is not None:
        db.close()


@app.errorhandler(HTTPException)
def handle_exception(e):
    # Log error and pass through
    if isinstance(e, HTTPException):
        get_structured_logger('server_error').error('Received HTTP exception', code=e.code, name=e.name, description=e.description)
    else:
        get_structured_logger('server_error').error('Received generic exception', exception=str(e))
    return e


def is_compatibility_mode() -> bool:
    """
    checks whether this request is in compatibility mode
    """
    return 'compatibility' in g and g.compatibility


def set_compatibility_mode():
    """
    sets the compatibility mode for this request
    """
    g.compatibility = True
