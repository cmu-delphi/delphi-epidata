from flask import Flask
from sqlalchemy.engine import Connection
from werkzeug.local import LocalProxy
from flask import g
from ._config import SECRET
from ._db import engine
from typing import cast

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
    db = g.pop("db", None)

    if db is not None:
        db.close()
