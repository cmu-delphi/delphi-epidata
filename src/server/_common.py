import os
from databases import Database
import sqlalchemy
from fastapi import FastAPI
from pydantic import BaseModel

# SQLAlchemy specific code, as with any other app
_DATABASE_URL = os.environ.get("API_DATABASE_URL", "sqlite:///./test.db")
_IS_TEST_DB = _DATABASE_URL.startswith("sqlite")

database = Database(_DATABASE_URL)
metadata = sqlalchemy.MetaData()

app = FastAPI()


@app.on_event("startup")
async def _startup():
    await database.connect()


@app.on_event("shutdown")
async def _shutdown():
    await database.disconnect()


def create_engine():
    engine = sqlalchemy.create_engine(
        _DATABASE_URL,
        connect_args={"check_same_thread": False}
        if _IS_TEST_DB
        else {},  # just for sqlite
    )
    if _IS_TEST_DB:
        metadata.create_all(engine)
    return engine
