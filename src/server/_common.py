from typing import cast

from flask import Flask, g
from sqlalchemy.engine import Connection
from werkzeug.local import LocalProxy

from ._config import SECRET
from ._db import engine

app = Flask("EpiData")
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


@app.teardown_appcontext
def teardown_db(exception=None):
    # close the db connection
    db = g.pop("db", None)

    if db is not None:
        db.close()
