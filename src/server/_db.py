from typing import Dict, List
from sqlalchemy import MetaData, create_engine, inspect
from sqlalchemy.engine import Engine
from sqlalchemy.engine.reflection import Inspector

from ._config import SQLALCHEMY_DATABASE_URI, SQLALCHEMY_ENGINE_OPTIONS

engine: Engine = create_engine(SQLALCHEMY_DATABASE_URI, **SQLALCHEMY_ENGINE_OPTIONS)
metadata = MetaData(bind=engine)
inspector: Inspector = inspect(engine)

TABLE_OPTIONS = dict(
    mysql_engine="InnoDB",
    # mariadb_engine="InnoDB",
    mysql_charset="utf8mb4",
    # mariadb_charset="utf8",
)


def sql_table_has_columns(table: str, columns: List[str]) -> bool:
    """
    checks whether the given table has all the given columns defined
    """
    table_columns: List[Dict] = inspector.get_columns(table)
    table_column_names = set(str(d.get("name", "")).lower() for d in table_columns)
    return all(c.lower() in table_column_names for c in columns)
