import re
from datetime import date, timedelta, datetime
from functools import wraps
from typing import Optional, cast
from uuid import uuid4

from flask import Response, g, request
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from werkzeug.local import LocalProxy
import redis

from ._common import app
from ._config import API_KEY_REQUIRED_STARTING_AT, RATELIMIT_STORAGE_URL, URL_PREFIX, REDIS_HOST
from ._params import extract_integers, extract_strings, extract_dates, parse_source_signal_sets, parse_geo_sets
from ._exceptions import MissingAPIKeyException, UnAuthenticatedException, ValidationFailedException
from .admin.models import User, UserRole

# from ._logger import get_structured_logger

API_KEY_HARD_WARNING = API_KEY_REQUIRED_STARTING_AT - timedelta(days=14)
API_KEY_SOFT_WARNING = API_KEY_HARD_WARNING - timedelta(days=14)

API_KEY_WARNING_TEXT = (
    "an api key will be required starting at {}, go to https://delphi.cmu.edu to request one".format(
        API_KEY_REQUIRED_STARTING_AT
    )
)

TESTING_MODE = app.config.get("TESTING", False)


# TODO: should be fixed
# def log_info(user: User, msg: str, *args, **kwargs) -> None:
#     logger = get_structured_logger("api_key_logs", filename="api_keys_log.log")
#     if user.is_authenticated:
#         if user.tracking:
#             logger.info(msg, *args, **dict(kwargs, api_key=user.api_key))
#         else:
#             logger.info(msg, *args, **dict(kwargs, apikey="*****"))
#     else:
#         logger.info(msg, *args, **kwargs)


def resolve_auth_token() -> Optional[str]:
    for n in ("auth", "api_key", "token"):
        if n in request.values:
            return request.values[n]
    # username password
    if request.authorization and request.authorization.username == "epidata":
        return request.authorization.password
    # bearer token authentication
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        return auth_header[len("Bearer ") :]
    return None


def register_new_key() -> str:
    api_key = str(uuid4())
    User.create_user(api_key=api_key)
    return api_key


def mask_apikey(path: str) -> str:
    # Function to mask API key query string from a request path
    regexp = re.compile(r"[\\?&]api_key=([^&#]*)")
    if regexp.search(path):
        path = re.sub(regexp, "&api_key=*****", path)
    return path


def require_api_key() -> bool:
    n = date.today()
    return n >= API_KEY_REQUIRED_STARTING_AT and not TESTING_MODE


def _get_current_user():
    if "user" not in g:
        api_key = resolve_auth_token()
        user = User.find_user(api_key=api_key)
        request_path = request.full_path
        if not user.is_authenticated:
            if require_api_key():
                raise MissingAPIKeyException
        if not user.tracking:
            request_path = mask_apikey(request_path)
        # TODO: add logging
        # log_info(user, "Get path", path=request_path)
        g.user = user
    return g.user


current_user: User = cast(User, LocalProxy(_get_current_user))


def show_soft_api_key_warning() -> bool:
    n = date.today()
    return not current_user.id and not TESTING_MODE and API_KEY_SOFT_WARNING < n < API_KEY_HARD_WARNING


def show_hard_api_key_warning() -> bool:
    n = date.today()
    return not current_user.id and n > API_KEY_HARD_WARNING and not TESTING_MODE


def register_user_role(role_name: str) -> None:
    UserRole.create_role(role_name)


def _is_public_route() -> bool:
    public_routes_list = ["lib", "admin", "version"]
    for route in public_routes_list:
        if request.path.startswith(f"{URL_PREFIX}/{route}"):
            return True
    return False


@app.before_request
def resolve_user():
    if _is_public_route():
        return
    # try to get the db
    try:
        _get_current_user()
    except MissingAPIKeyException as e:
        raise e
    except UnAuthenticatedException as e:
        raise e
    except:
        app.logger.error("user connection error", exc_info=True)
        if require_api_key():
            raise MissingAPIKeyException()
        else:
            g.user = User("anonymous")


def require_role(required_role: str):
    def decorator_wrapper(f):
        if not required_role:
            return f

        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user or not current_user.has_role(required_role):
                raise UnAuthenticatedException()
            return f(*args, **kwargs)

        return decorated_function

    return decorator_wrapper


def _resolve_tracking_key() -> str:
    token = resolve_auth_token()
    return token or get_remote_address()


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
    signals_allowlist = [
        "google-symptoms:s05_smoothed_search",
        "google-symptoms:s02_smoothed_search",
        "doctor-visits:smoothed_adj_cli",
        "chng:smoothed_adj_outpatient_flu",
        "quidel-covid-ag:covid_ag_smoothed_pct_positive",
        "jhu-csse:confirmed_7dav_incidence_prop",
        "hhs:confirmed_admissions_covid_1d_prop_7dav",
        "hhs:confirmed_admissions_influenza_1d_prop_7dav",
        "jhu-csse:deaths_7dav_incidence_prop",
        "fb-survey:smoothed_wcli",
        "fb-survey:smoothed_whh_cmnty_cli",
        "fb-survey:smoothed_wwearing_mask_7d",
        "fb-survey:smoothed_wothers_masked_public",
        "fb-survey:smoothed_wcovid_vaccinated_appointment_or_accept",
        "fb-survey:smoothed_winperson_school_fulltime_oldest",
        "fb-survey:smoothed_wshop_indoors_1d",
        "fb-survey:smoothed_wpublic_transit_1d",
        "fb-survey:smoothed_wwork_outside_home_indoors_1d",
        "fb-survey:smoothed_wspent_time_indoors_1d",
        "fb-survey:smoothed_wrestaurant_indoors_1d",
        "fb-survey:smoothed_wlarge_event_indoors_1d",
        "fb-survey:smoothed_wtravel_outside_state_7d",
        "fb-survey:smoothed_wanxious_7d",
        "fb-survey:smoothed_wdepressed_7d",
        "fb-survey:smoothed_wworried_catch_covid",
        "fb-survey:smoothed_wworried_finances",
        "fb-survey:smoothed_wtested_14d",
        "fb-survey:smoothed_wtested_positive_14d",
    ]
    request_signals = []
    if "signal" in request.args.keys():
        request_signals += extract_strings("signal")
    if "signals" in request.args.keys():
        request.signals += extract_strings("signals")
    return all([signal in signals_allowlist for signal in request_signals])


limiter = Limiter(app, key_func=_resolve_tracking_key, storage_uri=RATELIMIT_STORAGE_URL)


@limiter.request_filter
def _no_rate_limit() -> bool:
    if TESTING_MODE or _is_public_route():
        return False
    user = _get_current_user()
    if not user.is_authenticated:
        multiples = get_multiples_count(request)
        if multiples < 0:
            raise MissingAPIKeyException
        if multiples >= 0:
            if check_signals_allowlist(request):
                return True
            else:
                return False
    # no rate limit if user is registered
    return user is not None and user.registered  # type: ignore


@app.after_request
def update_key_last_time_used(response):
    if _is_public_route():
        return response
    try:
        r = redis.Redis(host=REDIS_HOST)
        api_key = g.user.api_key
        if api_key == "anonymous":
            api_key = _resolve_tracking_key()
        r.set(f"LAST_USED/{api_key}", datetime.strftime(datetime.now(), "%Y-%m-%d"))
    except Exception as e:
        print(e)  # TODO: should be handled properly
    finally:
        return response
