from sqlalchemy import MetaData, create_engine
from sqlalchemy.engine import Engine
from ._config import SQLALCHEMY_DATABASE_URI, SQLALCHEMY_ENGINE_OPTIONS

engine: Engine = create_engine(SQLALCHEMY_DATABASE_URI, **SQLALCHEMY_ENGINE_OPTIONS)
metadata = MetaData(bind=engine)
