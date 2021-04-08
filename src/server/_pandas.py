from typing import Dict, Any
import pandas as pd

from sqlalchemy import text

from ._common import engine
from ._printer import create_printer, APrinter
from ._query import filter_fields
from ._exceptions import DatabaseErrorException


def as_pandas(query: str, params: Dict[str, Any]) -> pd.DataFrame:
    try:
        return pd.read_sql_query(text(str(query)), engine, params=params)
    except Exception as e:
        raise DatabaseErrorException(str(e))


def print_pandas(df: pd.DataFrame):
    p = create_printer()

    def gen():
        for row in df.to_dict(orient="records"):
            yield row

    return p(filter_fields(gen()))
