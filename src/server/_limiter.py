from flask import Response, request, g
from flask_limiter import Limiter
from werkzeug.exceptions import Unauthorized

from delphi.epidata.server.endpoints.covidcast_utils.dashboard_signals import DashboardSignals

from ._common import app, get_real_ip_addr
from ._config import RATELIMIT_STORAGE_URL, RATE_LIMIT
from ._exceptions import ValidationFailedException
from ._params import extract_dates, extract_integers, extract_strings
from ._security import TESTING_MODE, _get_current_user, _is_public_route, resolve_auth_token


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
        "locations": extract_strings,
        "epiweeks": extract_integers,
        "flu_types": extract_strings,
        "states": extract_strings,
        "ccn": extract_strings,
        "city": extract_strings,
        "zip": extract_strings,
        "fips_code": extract_strings,
        "hospital_pks": extract_strings,
        "collection_weeks": extract_integers,
        "publication_dates": extract_strings,
        "dates": extract_integers,
        "issues": extract_integers,
        "time_types": extract_strings,
        "signals": extract_strings,
        "signal": extract_strings,
        "time_values": extract_dates,
        "sensor_names": extract_strings,
        "geo_values": extract_strings,
        "geo_value": extract_strings,
        "names": extract_strings,
        "regions": extract_strings,
        "articles": extract_strings,
    }
    multiple_selection_allowed = 2
    for k, v in request.args.items():
        if v == "*":
            multiple_selection_allowed -= 1
        try:
            vals = multiples.get(k)(k)
            if len(vals) >= 2:
                multiple_selection_allowed -= 1
        except ValidationFailedException:
            continue
        except TypeError:
            continue
    return multiple_selection_allowed


def check_signals_allowlist(request):
    signals_allowlist = {':'.join(ss_pair) for ss_pair in DashboardSignals().srcsig_list()}
    request_signals = []
    if "signal" in request.args.keys():
        request_signals += extract_strings("signal")
    if "signals" in request.args.keys():
        request_signals += extract_strings("signals")
    if len(request_signals) == 0:
        return False
    return all([signal in signals_allowlist for signal in request_signals])


def _resolve_tracking_key() -> str:
    token = resolve_auth_token()
    return token or get_real_ip_addr(request)


def get_host(endpoint_name):
    return request.host


limiter = Limiter(_resolve_tracking_key, app=app, storage_uri=RATELIMIT_STORAGE_URL)

host_limit = limiter.shared_limit(RATE_LIMIT, deduct_when=deduct_on_success, scope=get_host)


@limiter.request_filter
def _no_rate_limit() -> bool:
    if TESTING_MODE or _is_public_route():
        return False
    if not g.user.is_authenticated:
        multiples = get_multiples_count(request)
        if multiples < 0:
            raise Unauthorized
        if multiples >= 0:
            return check_signals_allowlist(request)
    # no rate limit if user is registered
    return g.user.api_key != "anonymous" and g.user.registered  # type: ignore
