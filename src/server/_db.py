from sqlalchemy import create_engine, MetaData
from sqlalchemy.engine import Engine
import redis
from sqlalchemy.orm import sessionmaker

from ._config import SQLALCHEMY_DATABASE_URI, SQLALCHEMY_DATABASE_URI_PRIMARY, SQLALCHEMY_ENGINE_OPTIONS, REDIS_HOST, REDIS_PASSWORD


# _db.py exists so that we dont have a circular dependency:
#   previously `_common` imported from `_security` which imported from `admin.models`, which imported (back again) from `_common` for database connection objects


engine: Engine = create_engine(SQLALCHEMY_DATABASE_URI, **SQLALCHEMY_ENGINE_OPTIONS)

if SQLALCHEMY_DATABASE_URI_PRIMARY:
    user_engine: Engine = create_engine(SQLALCHEMY_DATABASE_URI_PRIMARY, **SQLALCHEMY_ENGINE_OPTIONS)
else:
    user_engine: Engine = engine

metadata = MetaData(bind=user_engine)

Session = sessionmaker(bind=user_engine)

redis_conn_pool = redis.ConnectionPool(host=REDIS_HOST, password=REDIS_PASSWORD, max_connections=200)
redis_conn = redis.Redis(connection_pool=redis_conn_pool)


