from typing import Dict, List, Optional

from flask import Blueprint, request
from flask.json import loads
from sqlalchemy import text

from .._common import db
from .._params import extract_strings
from .._printer import create_printer
from .._query import filter_fields
from ..utils.logger import get_structured_logger

bp = Blueprint("covidcast_meta", __name__)


class SourceSignal:
    source: str
    signal: str

    def __init__(self, source_signal: str):
        split = source_signal.split(":", 2)
        self.source = split[0]
        self.signal = split[1] if len(split) > 1 else "*"

    def __str__(self):
        return f"{self.source}:{self.signal}"


def fetch_data(
    time_types: Optional[List[str]],
    geo_types: Optional[List[str]],
    signals: Optional[List[SourceSignal]],
):
    # complain if the cache is more than 75 minutes old
    max_age = 75 * 60

    row = db.execute(
        text(
            "SELECT UNIX_TIMESTAMP(NOW()) - timestamp AS age, epidata FROM covidcast_meta_cache LIMIT 1"
        )
    ).fetchone()

    if not row or not row["epidata"]:
        get_structured_logger('server_api').warning("no data in covidcast_meta cache")
        return

    age = row["age"]
    if age > max_age and row["epidata"]:
        get_structured_logger('server_api').warning("covidcast_meta cache is stale", cache_age=age)

    epidata = loads(row["epidata"])

    if not epidata:
        return

    def filter_row(row: Dict):
        if time_types and row.get("time_type") not in time_types:
            return False
        if geo_types and row.get("geo_type") not in geo_types:
            return False
        if not signals:
            return True
        for signal in signals:
            # match source and (signal or no signal or signal = *)
            if row.get("data_source") == signal.source and (
                signal.signal == "*" or signal.signal == row.get("signal")
            ):
                return True
        return False

    for row in epidata:
        if filter_row(row):
            yield row


@bp.route("/", methods=("GET", "POST"))
def handle():
    time_types = extract_strings("time_types")
    signals = [SourceSignal(v) for v in (extract_strings("signals") or [])]
    geo_types = extract_strings("geo_types")

    return create_printer(request.values.get("format"))(filter_fields(fetch_data(time_types, geo_types, signals)))
