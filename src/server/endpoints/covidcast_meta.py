from typing import Dict, List, Optional

from flask import Blueprint, request
from flask.json import loads
from sqlalchemy import text

from .._common import db
from .._params import extract_strings
from .._printer import create_printer
from .._query import filter_fields
from .._security import current_user, sources_protected_by_roles
from delphi_utils import get_structured_logger

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
    return (x for x in [])


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

    # the expected metadata regeneration interval in seconds, aka time between runs of
    # src/acquisition/covidcast/covidcast_meta_cache_updater.py (currently 2h)
    standard_age = 2 * 60 * 60
    # a short period when a client can continue to use this metadata even if its slightly stale,
    # which also gives some padding if the md generation is running slow,
    # and which also acts as a minimum cacheable time (currently 10 mins)
    age_margin = 10 * 60
    # these should be updated if a stale cache will have undue impact on user activities, such as
    # if we start updating the metadata table much more frequently and having up-to-the-minute
    # metadata accuracy becomes important to users once more.
    # TODO: get the above two values ^ from config vars?
    age = metadata["age"]
    reported_age = max(0, min(age, standard_age) - age_margin)

    user = current_user

    def cache_entry_gen():
        for entry in metadata_list:
            if time_types and entry.get("time_type") not in time_types:
                continue
            if geo_types and entry.get("geo_type") not in geo_types:
                continue
            entry_source = entry.get("data_source")
            if entry_source in sources_protected_by_roles:
                role = sources_protected_by_roles[entry_source]
                if not (user and user.has_role(role)):
                    # if this is a protected source
                    # and the user doesnt have the allowed role
                    # (or if we have no user)
                    # then skip this source
                    continue
            if not signals:
                yield entry
            for signal in signals:
                # match source and (signal or no signal or signal = *)
                if entry_source == signal.source and (
                    signal.signal == "*" or signal.signal == entry.get("signal")
                ):
                    yield entry

    return printer(
        filter_fields(cache_entry_gen()),
        headers={
            "Cache-Control": f"max-age={standard_age}, public",
            "Age": f"{reported_age}",
            # TODO?: "Expires": f"{}", # superseded by Cache-Control: https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Expires
        }
    )
