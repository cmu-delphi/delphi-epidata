from delphi.epidata.server.endpoints.covidcast_utils.dashboard_signals import DashboardSignals
from flask import Response, request
from flask_limiter import Limiter, HEADERS
from redis import Redis
from werkzeug.exceptions import Unauthorized, TooManyRequests

from ._common import app, get_real_ip_addr
from ._config import RATE_LIMIT, RATELIMIT_STORAGE_URL, REDIS_HOST, REDIS_PASSWORD
from ._exceptions import ValidationFailedException
from ._params import extract_dates, extract_integers, extract_strings, parse_source_signal_sets
from ._security import _is_public_route, current_user, resolve_auth_token, ERROR_MSG_RATE_LIMIT, ERROR_MSG_MULTIPLES



def deduct_on_success(response: Response) -> bool:
    if response.status_code != 200:
        return False
    # check if we have the classic format
    if not response.is_streamed and response.is_json:
        out = response.json
        if out and isinstance(out, dict) and out.get("result") == -1:
            return False
    return True


def get_multiples_count(request):
    multiples = {
        "articles": extract_strings,
        "ccn": extract_strings,
        "city": extract_strings,
        "collection_weeks": extract_integers,
        "dates": extract_integers,
        "epiweeks": extract_integers,
        "fips_code": extract_strings,
        "flu_types": extract_strings,
        "geo_value": extract_strings,
        "geo_values": extract_strings,
        "hospital_pks": extract_strings,
        "issues": extract_integers,
        "locations": extract_strings,
        "names": extract_strings,
        "publication_dates": extract_strings,
        "regions": extract_strings,
        "sensor_names": extract_strings,
        "signal": extract_strings,
        "signals": extract_strings,
        "states": extract_strings,
        "time_types": extract_strings,
        "time_values": extract_dates,
        "zip": extract_strings,
    }
    multiple_selection_allowed = 2
    if "window" in request.args.keys():
        multiple_selection_allowed -= 1
    for k, v in request.args.items():
        if "*" in v:
            multiple_selection_allowed -= 1
            continue
        try:
            vals = multiples.get(k)(k)
            if len(vals) >= 2:
                multiple_selection_allowed -= 1
            elif len(vals) and isinstance(vals, list) and isinstance(vals[0], tuple):
                # else we have one val which is a tuple, representing a range, and thus is a "multiple"
                multiple_selection_allowed -= 1
        except ValidationFailedException:
            continue
        except TypeError:
            continue
    return multiple_selection_allowed


def check_signals_allowlist(request):
    signals_allowlist = {":".join(ss_pair) for ss_pair in DashboardSignals().srcsig_list()}
    request_signals = set()
    try:
        source_signal_sets = parse_source_signal_sets()
    except ValidationFailedException:
        return False
    for source_signal in source_signal_sets:
        # source_signal.signal is expected to be eiter list or bool:
        # in case of bool, we have wildcard signal -> return False as there are no chances that
        # all signals from given source will be whitelisted
        # in case of list, we have list of signals
        if isinstance(source_signal.signal, bool):
            return False
        for signal in source_signal.signal:
            request_signals.add(f"{source_signal.source}:{signal}")
    if len(request_signals) == 0:
        return False
    return request_signals.issubset(signals_allowlist)


def _resolve_tracking_key() -> str:
    token = resolve_auth_token()
    return token or get_real_ip_addr(request)


limiter = Limiter(
    _resolve_tracking_key,
    app=app,
    storage_uri=RATELIMIT_STORAGE_URL,
    request_identifier=lambda: "EpidataLimiter",
    headers_enabled=True,
    header_name_mapping={
        HEADERS.LIMIT: "X-My-Limit",
        HEADERS.RESET: "X-My-Reset",
        HEADERS.REMAINING: "X-My-Remaining",
    },
)

apply_limit = limiter.limit(RATE_LIMIT, deduct_when=deduct_on_success)


@app.errorhandler(429)
def ratelimit_handler(e):
    return TooManyRequests(ERROR_MSG_RATE_LIMIT)


@limiter.request_filter
def _no_rate_limit() -> bool:
    if _is_public_route():
        # no rate limit for public routes
        return True
    if current_user:
        # no rate limit if user is registered
        return True

    multiples = get_multiples_count(request)
    if multiples < 0:
        # too many multiples
        raise Unauthorized(ERROR_MSG_MULTIPLES)
    return check_signals_allowlist(request)
