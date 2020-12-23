from typing import List, Optional
import sqlalchemy
from pydantic import BaseModel, Field
import json
import datetime
from fastapi import Depends
from enum import Enum

from ._utils import parse_str_list_generator
from ._common import app, metadata, database

covidcast_meta = sqlalchemy.Table(
    "covidcast_meta",
    metadata,
    sqlalchemy.Column("timestamp", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("epidata", sqlalchemy.String),
)


class TimeType(str, Enum):
    week = "week"
    day = "day"


class GeoType(str, Enum):
    nation = "nation"
    state = "state"
    msa = "msa"
    county = "county"
    hsa = "hsa"
    hss = "hsa"


class DataSourceSignal(BaseModel):
    data_source: str
    signal: str

    def __str__(self):
        return f"{self.data_source}:{self.signal}"


class COVIDcastMetaParameters(BaseModel):
    time_types: Optional[List[TimeType]] # TODO , encoded str
    geo_types: Optional[List[GeoType]] # TODO , encoded str
    signals: Optional[List[DataSourceSignal]]  # TODO encoded : and ,
    columns: Optional[List[str]] = Field(None, alias="fields") # TODO CSV encoded


class COVIDcastMetaRow(BaseModel):
    data_source: str
    signal: str
    geo_type: GeoType
    time_type: TimeType

    min_time: datetime.date
    max_time: datetime.date
    num_locations: int

    min_value: float
    max_value: float
    mean_value: float
    stdev_vaue: float

    last_update: int
    max_issue: datetime.date
    min_lag: int
    max_lag: int


def _covidcast_meta_impl(param: COVIDcastMetaParameters)

@app.get("/covidcast_meta/", response_model=List[COVIDcastMetaRow])
async def covidcast_meta():
    r = await database.fetch_one(
        """SELECT UNIX_TIMESTAMP(NOW()) - timestamp AS age, epidata FROM covidcast_meta_cache LIMIT 1"""
    )
    if not r:
        return []

    epidata: List[dict] = json.loads(r.epidata)

    p = COVIDcastMetaParameters()

    return epidata


# @app.post("/covidcast_meta/", response_model=List[COVIDcastMetaRow])
# async def _covidcast_meta_post():
#     query = covidcast.insert().values(text=note.text, completed=note.completed)
#     last_record_id = await database.execute(query)
#     return {**note.dict(), "id": last_record_id}