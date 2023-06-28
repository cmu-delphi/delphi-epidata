from typing import Dict, List, Optional

from flask import Blueprint, request
from flask.json import loads
from sqlalchemy import text

from .._common import db
from .._params import extract_strings
from .._printer import create_printer
from .._query import filter_fields
from delphi.epidata.common.logger import get_structured_logger

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


# empty generator that never yields
def _nonerator():
    return
    yield


@bp.route("/", methods=("GET", "POST"))
def handle():
    time_types = extract_strings("time_types")
    signals = [SourceSignal(v) for v in (extract_strings("signals") or [])]
    geo_types = extract_strings("geo_types")

    printer = create_printer(request.values.get("format"))

    metadata = db.execute(
        text(
            "SELECT UNIX_TIMESTAMP(NOW()) - timestamp AS age, epidata FROM covidcast_meta_cache LIMIT 1"
        )
    ).fetchone()

    if not metadata or "epidata" not in metadata:
        # the db table `covidcast_meta_cache` has no rows
        get_structured_logger('server_api').warning("no data in covidcast_meta cache")
        return printer(_nonerator())

    metadata_list = loads(metadata["epidata"])

    if not metadata_list:
        # the db table has a row, but there is no metadata about any signals in it
        get_structured_logger('server_api').warning("empty entry in covidcast_meta cache")
        return printer(_nonerator())

    standard_age = 60 * 60 # expected metadata regeneration interval, in seconds (currently 60 mins)
    # TODO: get this ^ from a config var?  ideally, it should be set to the time between runs of
    #       src/acquisition/covidcast/covidcast_meta_cache_updater.py
    age = metadata["age"]
    if age > standard_age * 1.25:
        # complain if the cache is too old (currently, more than 75 mins old)
        get_structured_logger('server_api').warning("covidcast_meta cache is stale", cache_age=age)

    def cache_entry_gen():
        for entry in metadata_list:
            if time_types and row.get("time_type") not in time_types:
                continue
            if geo_types and row.get("geo_type") not in geo_types:
                continue
            if not signals:
                yield entry
            for signal in signals:
                # match source and (signal or no signal or signal = *)
                if row.get("data_source") == signal.source and (
                    signal.signal == "*" or signal.signal == row.get("signal")
                ):
                    yield entry

    return printer(
        filter_fields(cache_entry_gen()),
        headers={
            "Cache-Control": f"max-age={standard_age}, public",
            "Age": f"{age}",
            # TODO?: "Expires": f"{}", # superseded by Cache-Control: https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Expires
        }
    )
