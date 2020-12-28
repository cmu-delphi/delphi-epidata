from flask import Flask
from sqlalchemy.engine import Connection
from werkzeug.local import LocalProxy
from flask import g
from . import _config as default_config
from ._db import engine

app = Flask("EpiData")
app.config.from_object(default_config)


def _get_db() -> Connection:
    if "db" not in g:
        conn = engine.connect()
        g.db = conn
    return g.db


"""
access to the SQL Alchemy connection for this request
"""
db: Connection = LocalProxy(_get_db)


@app.teardown_appcontext
def teardown_db(exception=None):
    db = g.pop("db", None)

    if db is not None:
        db.close()
