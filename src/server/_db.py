from sqlalchemy import create_engine, MetaData
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker

from ._config import SQLALCHEMY_DATABASE_URI, SQLALCHEMY_DATABASE_URI_PRIMARY, SQLALCHEMY_ENGINE_OPTIONS


# _db.py exists so that we dont have a circular dependency:
#   previously `_common` imported from `_security` which imported from `admin.models`, which imported (back again) from `_common` for database connection objects


engine: Engine = create_engine(SQLALCHEMY_DATABASE_URI, **SQLALCHEMY_ENGINE_OPTIONS)
metadata = MetaData(bind=engine)
Session = sessionmaker(bind=engine)

if SQLALCHEMY_DATABASE_URI_PRIMARY:
    write_engine: Engine = create_engine(SQLALCHEMY_DATABASE_URI_PRIMARY, **SQLALCHEMY_ENGINE_OPTIONS)
    write_metadata = MetaData(bind=write_engine)
    WriteSession = sessionmaker(bind=write_engine)
else:
    write_engine: Engine = engine
    write_metadata = metadata
    WriteSession = Session
