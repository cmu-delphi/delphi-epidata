from sqlalchemy import Table, Column, String, Integer, DateTime, func
from ._db import metadata, TABLE_OPTIONS
from flask import request
from ._common import db

analytics_table = Table(
    "api_analytics",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("datetime", DateTime),
    Column("ip", String(15)),
    Column("ua", String(1024)),
    Column("source", String(32)),
    Column("result", Integer),
    Column("num_rows", Integer),
    **TABLE_OPTIONS
)


def _derive_endpoint():
    endpoint = request.values.get("endpoint", request.values.get("source"))
    if endpoint:
        return endpoint
    # guess from path
    path: str = request.path
    if path.startswith("/"):
        path = path[1:]
    if path.endswith("/"):
        path = path[:-1]
    if path == "api.php":
        return ""
    return path


def record_analytics(result: int, num_rows=0):
    ip = request.headers.get(
        "HTTP_X_FORWARDED_FOR", request.headers.get("REMOTE_ADDR", "")
    )
    ua = request.headers.get("HTTP_USER_AGENT", "")
    endpoint = _derive_endpoint()

    stmt = analytics_table.insert().values(
        datetime=func.now(),
        source=endpoint,
        ip=ip,
        ua=ua,
        result=result,
        num_rows=num_rows,
    )

    db.execution_options(stream_results=False).execute(stmt)