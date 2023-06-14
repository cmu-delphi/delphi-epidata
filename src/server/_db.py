from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker

from ._config import SQLALCHEMY_DATABASE_URI, SQLALCHEMY_DATABASE_URI_PRIMARY, SQLALCHEMY_ENGINE_OPTIONS


# _db.py exists so that we dont have a circular dependency:
#   previously `_common` imported from `_security` which imported from `admin.models`, which imported (back again) from `_common` for database connection objects


engine: Engine = create_engine(SQLALCHEMY_DATABASE_URI, **SQLALCHEMY_ENGINE_OPTIONS, execution_options={'engine_id': 'default'})
Session = sessionmaker(bind=engine)

if SQLALCHEMY_DATABASE_URI_PRIMARY and SQLALCHEMY_DATABASE_URI_PRIMARY != SQLALCHEMY_DATABASE_URI:
    # TODO: insert log statement about this?
    write_engine: Engine = create_engine(SQLALCHEMY_DATABASE_URI_PRIMARY, **SQLALCHEMY_ENGINE_OPTIONS, execution_options={'engine_id': 'write_engine'})
    WriteSession = sessionmaker(bind=write_engine)
else:
    write_engine: Engine = engine
    WriteSession = Session
