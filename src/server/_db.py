from sqlalchemy import MetaData, create_engine
from sqlalchemy.engine import Engine

from ._config import SQLALCHEMY_DATABASE_URI, SQLALCHEMY_ENGINE_OPTIONS

engine: Engine = create_engine(SQLALCHEMY_DATABASE_URI, **SQLALCHEMY_ENGINE_OPTIONS)
metadata = MetaData(bind=engine)

TABLE_OPTIONS = dict(
    mysql_engine="InnoDB",
    # mariadb_engine="InnoDB",
    mysql_charset="utf8mb4",
    # mariadb_charset="utf8",
)
