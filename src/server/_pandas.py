from typing import Any, Dict, Optional

import pandas as pd
from flask import request
from sqlalchemy import text
from sqlalchemy.engine.base import Engine

from ._common import engine
from ._config import MAX_RESULTS
from ._exceptions import DatabaseErrorException
from ._printer import create_printer
from ._query import filter_fields, limit_query


def as_pandas(
    query: str,
    params: Dict[str, Any],
    db_engine: Engine = engine,
    parse_dates: Optional[Dict[str, str]] = None,
    limit_rows=MAX_RESULTS+1
) -> pd.DataFrame:
    try:
        query = limit_query(query, limit_rows)
        return pd.read_sql_query(text(str(query)), db_engine, params=params, parse_dates=parse_dates)
    except Exception as e:
        raise DatabaseErrorException(str(e))


def print_pandas(df: pd.DataFrame):
    p = create_printer(request.values.get("format"))

    def gen():
        for row in df.to_dict(orient="records"):
            yield row

    return p(filter_fields(gen()))
