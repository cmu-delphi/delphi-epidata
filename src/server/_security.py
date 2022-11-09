from typing import Dict, List, Optional, Set, cast
from datetime import date, timedelta
from functools import wraps
from uuid import uuid4
from flask import g, Response
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from werkzeug.local import LocalProxy
from sqlalchemy import Table, Column, String, Integer, Boolean
from ._config import API_KEY_REQUIRED_STARTING_AT, RATELIMIT_STORAGE_URL, URL_PREFIX, UserRole
from ._common import app, request, db
from ._exceptions import MissingAPIKeyException, UnAuthenticatedException
from ._db import metadata, TABLE_OPTIONS

# This module is delivered by Dockerfile (devops/Dockerfile)
from ._logger import get_structured_logger
import re

API_KEY_HARD_WARNING = API_KEY_REQUIRED_STARTING_AT - timedelta(days=14)
API_KEY_SOFT_WARNING = API_KEY_HARD_WARNING - timedelta(days=14)

API_KEY_WARNING_TEXT = (
    "an api key will be required starting at {}, go to https://delphi.cmu.edu to request one".format(
        API_KEY_REQUIRED_STARTING_AT
    )
)

TESTING_MODE = app.config.get("TESTING", False)


# This user_table is defined here to interact with it inside DBUser class.
user_table = Table(
    "api_user",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("api_key", String(50), unique=True),
    Column("email", String(100)),
    Column("roles", String(255)),
    Column("tracking", Boolean(), default=True),
    Column("registered", Boolean(), default=False),
    **TABLE_OPTIONS,
)


class AbstractUser:
    """
    This is common user class
    """

    id: int
    api_key: str
    email: str
    roles: Set[str]
    tracking: bool = True
    registered: bool = False

    @staticmethod
    def find_by_api_key(api_key: int):
        stmt = user_table.select().where(user_table.c.api_key == api_key)
        user = db.execution_options(stream_results=False).execute(stmt).first()
        return user


class DBUser(AbstractUser):

    """
    This class is just a wrapper to ineract with `api_user` table.
    It contains all needed methods to execute CRUD queries and to find/list users.
    """

    @property
    def roles_str(self):
        return "\n".join(self.roles)

    @staticmethod
    def _parse(r: Dict) -> "DBUser":
        u = DBUser()
        u.id = r["id"]
        u.api_key = r["api_key"]
        u.email = r["email"]
        u.roles = set(r["roles"].split(","))
        u.tracking = r["tracking"] != False
        u.registered = r["registered"] == True
        return u

    @staticmethod
    def find(user_id: int) -> "DBUser":
        stmt = user_table.select().where(user_table.c.id == user_id)
        return DBUser._parse(db.execution_options(stream_results=False).execute(stmt).first())

    @staticmethod
    def find_by_api_key(api_key: int):
        user = AbstractUser.find_by_api_key(api_key)
        if user is None:
            return None
        return DBUser._parse(user)

    @staticmethod
    def list() -> List["DBUser"]:
        return [DBUser._parse(r) for r in db.execution_options(stream_results=False).execute(user_table.select())]

    @staticmethod
    def insert(api_key: str, email: str, roles: Set[str], tracking: bool = True, registered: bool = False):
        db.execute(
            user_table.insert().values(
                api_key=api_key, email=email, roles=",".join(roles), tracking=tracking, registered=registered
            )
        )

    def delete(self):
        db.execute(user_table.delete(user_table.c.id == self.id))

    @staticmethod
    def register_new_key() -> str:
        api_key = str(uuid4())
        DBUser.insert(api_key, "", set(), True, False)
        return api_key

    def update(
        self, api_key: str, email: str, roles: Set[str], tracking: bool = True, registered: bool = False
    ) -> "DBUser":
        db.execute(
            user_table.update()
            .where(user_table.c.id == self.id)
            .values(api_key=api_key, email=email, roles=",".join(roles), tracking=tracking, registered=registered)
        )
        self.api_key = api_key
        self.email = email
        self.roles = roles
        self.tracking = tracking
        self.registered = registered
        return self


class APIUser(AbstractUser):
    def __init__(
        self,
        api_key: str,
        email: str,
        authenticated: bool,
        roles: Set[str],
        tracking: bool = True,
        registered: bool = False,
    ) -> None:
        self.api_key = api_key
        self.email = email
        self.authenticated = authenticated
        self.roles = roles
        self.tracking = tracking
        self.registered = registered

    @staticmethod
    def get_anonymous_user():
        return APIUser("anonymous", "", False, set())

    @staticmethod
    def find_by_api_key(api_key: int):
        user = AbstractUser.find_by_api_key(api_key)
        if user is None:
            return APIUser.get_anonymous_user()
        return APIUser(user.api_key, user.email, True, set(user.roles.split(",")), user.tracking, user.registered)

    def get_apikey(self) -> str:
        return self.api_key

    def is_authenticated(self) -> bool:
        return self.authenticated

    def has_role(self, role: UserRole) -> bool:
        return role in self.roles

    def is_rate_limited(self) -> bool:
        return not self.registered

    def is_tracking(self) -> bool:
        return self.tracking

    def log_info(self, msg: str, *args, **kwargs) -> None:
        # Use structured logger instead of base logger
        logger = get_structured_logger("api_key_logs", filename="api_key_logs.log")
        if self.is_authenticated():
            if self.is_tracking():
                logger.info(msg, *args, **dict(kwargs, apikey=self.get_apikey()))
            else:
                logger.info(msg, *args, **dict(kwargs, apikey="*****"))
        else:
            # app.logger.info(msg, *args, **kwargs)
            logger.info(msg, *args, **kwargs)


def resolve_auth_token() -> Optional[str]:
    for name in ("auth", "api_key", "token"):
        if name in request.values:
            return request.values[name]
    # user name password
    if request.authorization and request.authorization.username == "epidata":
        return request.authorization.password
    # bearer token authentication
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        return auth_header[len("Bearer ") :]
    return None


def mask_apikey(path: str) -> str:
    # Function to mask API key query string from a request path
    regexp = re.compile(r"[\\?&]api_key=([^&#]*)")
    if regexp.search(path):
        path = re.sub(regexp, "&api_key=*****", path)
    return path


def require_api_key() -> bool:
    n = date.today()
    return n >= API_KEY_REQUIRED_STARTING_AT and not TESTING_MODE


def _get_current_user() -> APIUser:
    if "user" not in g:
        api_key = resolve_auth_token()
        user = APIUser.find_by_api_key(api_key)
        request_path = request.full_path
        if not user.is_authenticated() and require_api_key():
            raise MissingAPIKeyException()
        # If the user configured no-track option, mask the API key
        if not user.is_tracking():
            request_path = mask_apikey(request_path)
        user.log_info("Get path", path=request_path)
        g.user = user
    return g.user


current_user: APIUser = cast(APIUser, LocalProxy(_get_current_user))


def show_soft_api_key_warning() -> bool:
    n = date.today()
    return (
        not current_user.is_authenticated()
        and not TESTING_MODE
        and n > API_KEY_SOFT_WARNING
        and n < API_KEY_HARD_WARNING
    )


def show_hard_api_key_warning() -> bool:
    n = date.today()
    return not current_user.is_authenticated() and n > API_KEY_HARD_WARNING and not TESTING_MODE


def _is_public_route() -> bool:
    return (
        request.path.startswith(f"{URL_PREFIX}/lib")
        or request.path.startswith(f"{URL_PREFIX}/admin")
        or request.path.startswith(f"{URL_PREFIX}/version")
    )


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
            g.user = APIUser.get_anonymous_user()


def require_role(required_role: Optional[UserRole]):
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


limiter = Limiter(app, key_func=_resolve_tracking_key, storage_uri=RATELIMIT_STORAGE_URL)


@limiter.request_filter
def _no_rate_limit() -> bool:
    if TESTING_MODE or _is_public_route():
        return False
    # no rate limit if the user is registered
    user = _get_current_user()
    return user is not None and not user.is_rate_limited()
