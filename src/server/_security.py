from datetime import date, datetime, timedelta
from functools import wraps
from typing import Optional, cast

import redis
from delphi.epidata.common.logger import get_structured_logger
from flask import g, request
from werkzeug.exceptions import Unauthorized
from werkzeug.local import LocalProxy

from ._config import (
    API_KEY_REQUIRED_STARTING_AT,
    REDIS_HOST,
    REDIS_PASSWORD,
    API_KEY_REGISTRATION_FORM_LINK_LOCAL,
    TEMPORARY_API_KEY,
    URL_PREFIX,
)
from .admin.models import User, UserRole

API_KEY_HARD_WARNING = API_KEY_REQUIRED_STARTING_AT - timedelta(days=14)
API_KEY_SOFT_WARNING = API_KEY_HARD_WARNING - timedelta(days=14)

# rollout warning messages
# intended usage: in place of API_KEY_WARNING_TEXT
# phase 1 / soft warning: ROLLOUT_WARNING_RATE_LIMIT or ROLLOUT_WARNING_MULTIPLES
# phase 2 / hard warning: (ROLLOUT_WARNING_RATE_LIMIT + PHASE_2_STOPGAP) or (ROLLOUT_WARNING_MULTIPLES + PHASE_2_STOPGAP)

ROLLOUT_WARNING_RATE_LIMIT = "This request exceeded the anonymous limit on requests per minute."
ROLLOUT_WARNING_MULTIPLES = "This request exceeded the anonymous limit on selected multiples."
_ROLLOUT_WARNING_AD_FRAGMENT = "To be exempt from this limit, authenticate your requests with an API key, which will be enforced starting {}. Registration now available at {}.".format(
    API_KEY_REQUIRED_STARTING_AT, API_KEY_REGISTRATION_FORM_LINK_LOCAL
)

PHASE_1_2_STOPGAP = (  # todo: add temporary key
    "A temporary public key `{}` is available for use between now and {} to give you time to register or adapt your requests without this message continuing to break your systems."
).format(TEMPORARY_API_KEY, API_KEY_REQUIRED_STARTING_AT)


# steady-state error messages
ERROR_MSG_RATE_LIMIT = "Rate limit exceeded for anonymous queries.\nTo remove this limit, register a free API key at {}".format(API_KEY_REGISTRATION_FORM_LINK_LOCAL)
ERROR_MSG_MULTIPLES = "Requested too many multiples for anonymous queries.\nTo remove this limit, register a free API key at {}".format(API_KEY_REGISTRATION_FORM_LINK_LOCAL)
ERROR_MSG_INVALID_KEY = (
    "API key does not exist. Register a new key at {} or contact $CONTACT_POINT to troubleshoot".format(API_KEY_REGISTRATION_FORM_LINK_LOCAL)
)
ERROR_MSG_INVALID_ROLE = "Provided API key does not have access to this endpoint, please contact $CONTACT_POINT."


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


def show_no_api_key_warning() -> bool:
    # aka "phase 0"
    n = date.today()
    return not current_user and n < API_KEY_SOFT_WARNING


def show_soft_api_key_warning() -> bool:
    # aka "phase 1"
    n = date.today()
    return not current_user and API_KEY_SOFT_WARNING <= n < API_KEY_HARD_WARNING


def show_hard_api_key_warning() -> bool:
    # aka "phase 2"
    n = date.today()
    return not current_user and API_KEY_HARD_WARNING <= n < API_KEY_REQUIRED_STARTING_AT


def require_api_key() -> bool:
    # aka "phase 3"
    n = date.today()
    return API_KEY_REQUIRED_STARTING_AT <= n


def _get_current_user():
    if "user" not in g:
        api_key = resolve_auth_token()
        g.user = User.find_user(api_key=api_key)
    return g.user


current_user: User = cast(User, LocalProxy(_get_current_user))


def register_user_role(role_name: str) -> None:
    UserRole.create_role(role_name)


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


def update_key_last_time_used(user):
    if user:
        # update last usage for this user's api key to "now()"
        r = redis.Redis(host=REDIS_HOST, password=REDIS_PASSWORD)
        r.set(f"LAST_USED/{user.api_key}", datetime.strftime(datetime.now(), "%Y-%m-%d"))
