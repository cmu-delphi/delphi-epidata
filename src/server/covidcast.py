from typing import List
import sqlalchemy
from pydantic import BaseModel

from ._common import app, metadata, database

covidcast = sqlalchemy.Table(
    "covidcast",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("text", sqlalchemy.String),
    sqlalchemy.Column("completed", sqlalchemy.Boolean),
)


class CovidcastParameters(BaseModel):
    text: str
    completed: bool


class CovidcastRow(BaseModel):
    id: int
    text: str
    completed: bool


@app.get("/covidcast/", response_model=List[Note])
async def read_notes():
    query = covidcast.select()
    return await database.fetch_all(query)


@app.post("/covidcast/", response_model=Note)
async def create_note(note: NoteIn):
    query = covidcast.insert().values(text=note.text, completed=note.completed)
    last_record_id = await database.execute(query)
    return {**note.dict(), "id": last_record_id}