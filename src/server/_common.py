from typing import cast

from flask import Flask, g, request
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


"""
access to the SQL Alchemy connection for this request
"""
db: Connection = cast(Connection, LocalProxy(_get_db))


@app.before_request
def connect_db():
    if request.path.startswith('/lib'):
        return
    # try to get the db
    try:
        _get_db()
    except:
        raise DatabaseErrorException()


@app.teardown_appcontext
def teardown_db(exception=None):
    # close the db connection
    db = g.pop("db", None)

    if db is not None:
        db.close()
