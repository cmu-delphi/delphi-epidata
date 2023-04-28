import re
from datetime import date, datetime, timedelta
from functools import wraps
from typing import Optional, cast
from uuid import uuid4

import redis
from flask import g, request
from werkzeug.local import LocalProxy
from werkzeug.exceptions import Unauthorized

from ._common import app, get_real_ip_addr
from ._config import API_KEY_REQUIRED_STARTING_AT, REDIS_HOST, URL_PREFIX
from ._exceptions import MissingAPIKeyException, UnAuthenticatedException
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
                raise Unauthorized
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
            raise Unauthorized
        else:
            g.user = User("anonymous")


def require_role(required_role: str):
    def decorator_wrapper(f):
        if not required_role:
            return f

        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user or not current_user.has_role(required_role):
                raise Unauthorized
            return f(*args, **kwargs)

        return decorated_function

    return decorator_wrapper


@app.after_request
def update_key_last_time_used(response):
    if _is_public_route():
        return response
    try:
        r = redis.Redis(host=REDIS_HOST)
        api_key = g.user.api_key
        if api_key == "anonymous":
            api_key = get_real_ip_addr(request)
        r.set(f"LAST_USED/{api_key}", datetime.strftime(datetime.now(), "%Y-%m-%d"))
    except Exception as e:
        app.logger.error("User connection error. Last usage was not updated.", exc_info=False)
    finally:
        return response
