from datetime import date, datetime, timedelta
from functools import wraps
from typing import Optional, cast

import redis
from delphi_utils import get_structured_logger
from flask import g, request
from werkzeug.exceptions import Unauthorized
from werkzeug.local import LocalProxy

from ._config import (
    REDIS_HOST,
    REDIS_PASSWORD,
    API_KEY_REGISTRATION_FORM_LINK_LOCAL,
    URL_PREFIX,
)
from .admin.models import User


# steady-state error messages
ERROR_MSG_RATE_LIMIT = "Rate limit exceeded for anonymous queries. To remove this limit, register a free API key at {}".format(API_KEY_REGISTRATION_FORM_LINK_LOCAL)
ERROR_MSG_MULTIPLES = "Requested too many multiples for anonymous queries. To remove this limit, register a free API key at {}".format(API_KEY_REGISTRATION_FORM_LINK_LOCAL)
ERROR_MSG_INVALID_KEY = (
    "API key does not exist. Register a new key at {} or contact delphi-support+privacy@andrew.cmu.edu to troubleshoot".format(API_KEY_REGISTRATION_FORM_LINK_LOCAL)
)
ERROR_MSG_INVALID_ROLE = "Provided API key does not have access to this endpoint. Please contact delphi-support+privacy@andrew.cmu.edu."


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


def _get_current_user():
    if "user" not in g:
        api_key = resolve_auth_token()
        if api_key:
            g.user = User.find_user(api_key=api_key)
        else:
            g.user = None
    return g.user


current_user: User = cast(User, LocalProxy(_get_current_user))


def _is_public_route() -> bool:
    public_routes_list = ["lib", "admin", "version"]
    for route in public_routes_list:
        if request.path.startswith(f"{URL_PREFIX}/{route}"):
            return True
    return False


def require_role(required_role: str):
    def decorator_wrapper(f):
        if not required_role:
            return f

        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user or not current_user.has_role(required_role):
                get_structured_logger("api_security").info(
                    ERROR_MSG_INVALID_ROLE,
                    role=required_role,
                    api_key=(current_user and current_user.api_key),
                )
                raise Unauthorized(ERROR_MSG_INVALID_ROLE)
            return f(*args, **kwargs)

        return decorated_function

    return decorator_wrapper


# key is data "source" name, value is role name required to access that source
sources_protected_by_roles = {
    'quidel': 'quidel',
    # the following two entries are needed because
    # the covidcast endpoint uses this method
    # to allow using various different "source" name aliases:
    #     delphi.epidata.server.endpoints.covidcast_utils.model.create_source_signal_alias_mapper()
    # which, for reference, is populated by the file:
    #     src/server/endpoints/covidcast_utils/db_sources.csv
    'quidel-covid-ag': 'quidel',
    'quidel-flu': 'quidel',
}
# TODO(<insert gh issue link here>): source this info from a better place than a hardcoded dict:
#     maybe somewhere in the db?  maybe in src/server/endpoints/covidcast_utils/db_sources.csv ?


def update_key_last_time_used(user):
    if user:
        # update last usage for this user's api key to "now()"
        # TODO: consider making this call asynchronously
        r = redis.Redis(host=REDIS_HOST, password=REDIS_PASSWORD)
        r.set(f"LAST_USED/{user.api_key}", datetime.strftime(datetime.now(), "%Y-%m-%d"))
