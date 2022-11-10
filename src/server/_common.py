from typing import cast
import time

from flask import Flask, g, request
from sqlalchemy import event
from sqlalchemy.engine import Connection
from werkzeug.local import LocalProxy

from ._config import SECRET
from ._db import engine
from ._exceptions import DatabaseErrorException

app = Flask("EpiData", static_url_path="")
app.config["SECRET"] = SECRET


def _get_db() -> Connection:
    if "db" not in g:
        conn = engine.connect()
        g.db = conn
    return g.db

def log_and_raise_exception(message):
    app.logger.error(message)
    log_and_raise_exception(message)

"""
access to the SQL Alchemy connection for this request
"""
db: Connection = cast(Connection, LocalProxy(_get_db))

@event.listens_for(engine, "before_cursor_execute")
def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    t = time.time()
    # TODO: probbly just use one of these two:
    context._query_start_time = t
    conn.info.setdefault('query_start_time', []).append(t)


@event.listens_for(engine, "after_cursor_execute")
def after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    # this timing info may be suspect, at least in terms of dmbs cpu time...
    # it is likely that it includes that time as well as any overhead that
    # come from throttling or flow control on the streamed data, as well as
    # any row transform/processing time
    t = time.time()
    total_cntx = t - context._query_start_time
    total_cnxn = t - conn.info['query_start_time'].pop(-1)
    # Convert to milliseconds
    total_cntx = total_cntx * 1000
    total_cnxn = total_cnxn * 1000
    app.logger.info("SQL execute() elapsed time: %s", str(dict(
        statement=statement, total_cntx=total_cntx, total_cnxn=total_cnxn)))

@app.before_request
def connect_db():
    if request.path.startswith('/lib'):
        return
    # try to get the db
    try:
        _get_db()
    except:
        app.logger.error('database connection error', exc_info=True)
        raise DatabaseErrorException()

@app.before_request
def log_request_info():
    app.logger.info('Received API request: %s', str(dict(method=request.method, path=request.full_path, args=request.args)))

@app.before_request
def time_request_start():
    t = time.time()
    g._request_start_time = t

@app.after_request
def time_request_end(response):
    t = time.time()
    total_time = t - g._request_start_time
    # Convert to milliseconds
    total_time = total_time * 1000
    app.logger.info('API request elapsed time: %s', str(dict(method=request.method, path=request.full_path, args=request.args, time=total_time)))
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
