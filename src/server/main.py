from typing import Optional
from fastapi import FastAPI, HTTPException

from ._common import create_engine, app
from .covidcast_meta import covidcast_meta

__all__ = ["app"]

engine = create_engine()


@app.get("/api.php")
def handle_generic(
    endpoint: Optional[str] = None, source: Optional[str] = None, **kwargs
):
    # if not endpoint and not source:
    raise HTTPException(401, detail=dict(a=5))
