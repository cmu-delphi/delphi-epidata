from typing import cast
import time

from flask import Flask, g, request
from sqlalchemy import event
from sqlalchemy.engine import Connection
from werkzeug.local import LocalProxy

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

def log_and_raise_validation_exception(message):
    get_structured_logger('server_error').error(message)
    raise ValidationFailedException(message)

"""
access to the SQL Alchemy connection for this request
"""
db: Connection = cast(Connection, LocalProxy(_get_db))

@event.listens_for(engine, "before_cursor_execute")
def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    t = time.time()
    context._query_start_time = t


@event.listens_for(engine, "after_cursor_execute")
def after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    # this timing info may be suspect, at least in terms of dbms cpu time...
    # it is likely that it includes that time as well as any overhead that
    # comes from throttling or flow control on the streamed data, as well as
    # any row transform/processing time
    t = time.time()
    total_time = t - context._query_start_time

    # Convert to milliseconds
    total_time = total_time * 1000
    get_structured_logger('server_api').info("Executed timed SQL query", statement=statement, total_time=total_time)


@app.before_request
def before_request_execute():
    if request.path.startswith('/lib'):
        return
    # try to get the db
    try:
        _get_db()
    except Exception as e:
        get_structured_logger('server_error').error('database connection error', exception=e)
        raise DatabaseErrorException()

    # Log statement
    get_structured_logger('server_api').info("Received API request", method=request.method, path=request.full_path, args=request.args)

    # Set timer for statement
    t = time.time()
    g._request_start_time = t


@app.after_request
def after_request_execute(response):
    t = time.time()
    total_time = t - g._request_start_time
    # Convert to milliseconds
    total_time = total_time * 1000
    get_structured_logger('server_api').info('Executed timed API request', method=request.method, path=request.full_path, args=request.args, response_status=response.status, response_body=response.response, time=total_time)
    return response


@app.teardown_appcontext
def teardown_db(exception=None):
    # close the db connection
    db = g.pop("db", None)

    if db is not None:
        db.close()


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
