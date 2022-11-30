import re
from datetime import timedelta, date
from functools import wraps
from typing import Set, Optional, List, Dict, cast
from uuid import uuid4

from flask import g, Response
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from sqlalchemy import Column, Integer, String, Boolean, delete, update, Table, select
from sqlalchemy.exc import IntegrityError
from werkzeug.local import LocalProxy

from ._common import request, app, db
from ._config import URL_PREFIX, RATELIMIT_STORAGE_URL, API_KEY_REQUIRED_STARTING_AT
from ._db import metadata
from ._exceptions import MissingAPIKeyException, UnAuthenticatedException
from ._logger import get_structured_logger

API_KEY_HARD_WARNING = API_KEY_REQUIRED_STARTING_AT - timedelta(days=14)
API_KEY_SOFT_WARNING = API_KEY_HARD_WARNING - timedelta(days=14)

API_KEY_WARNING_TEXT = "an api key will be required starting at {}, go to https://delphi.cmu.edu to request one".format(
    API_KEY_REQUIRED_STARTING_AT
)

TESTING_MODE = app.config.get("TESTING", False)

api_user_table = Table(
    "api_user",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("api_key", String(50), unique=True),
    Column("tracking", Boolean, default=True),
    Column("registered", Boolean, default=False)
)

user_role_table = Table(
    "user_role",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("name", String(50), unique=True)
)

user_role_link_table = Table(
    "user_role_link",
    metadata,
    Column("user_id", Integer, primary_key=True),
    Column("role_id", Integer, primary_key=True)
)


class APIUser:
    id: int
    api_key: str
    authenticated: bool = False
    roles: Set[str] = set()
    tracking: bool = True
    registered: bool = False

    @staticmethod
    def get_user_roles(user_id: int) -> Set[str]:
        user_role_ids = db.execute(
            select(user_role_link_table.c.role_id)
            .where(user_role_link_table.c.user_id == user_id)
        ).fetchall()
        user_roles = db.execute(
            select(user_role_table.c.name)
            .where(user_role_table.c.id.in_([role.role_id for role in user_role_ids]))
        ).fetchall()
        return set([role.name for role in user_roles])

    @property
    def roles_str(self):
        return "\n".join(self.roles)

    @staticmethod
    def _parse(r: Dict) -> "APIUser":
        u = APIUser()
        u.id = r["id"]
        u.api_key = r["api_key"]
        u.authenticated = True
        u.roles = APIUser.get_user_roles(r["id"])
        u.tracking = r["tracking"] != False
        u.registered = r["registered"] == True
        return u

    @staticmethod
    def find_user(user_id: Optional[int] = None, api_key: Optional[str] = None) -> Optional["APIUser"]:
        stmt = None
        if user_id is not None:
            stmt = api_user_table.select().where(api_user_table.c.id == user_id)
        if api_key is not None:
            stmt = api_user_table.select().where(api_user_table.c.api_key == api_key)
        user = db.execute(stmt).first() if stmt is not None else APIUser.get_anonymous_user()
        if user is None:
            return APIUser.get_anonymous_user()
        return APIUser._parse(user) if user.api_key != "anonymous" else user

    @staticmethod
    def list() -> List["APIUser"]:
        stmt = api_user_table.select()
        return [APIUser._parse(u) for u in db.execute(stmt).all()]

    @staticmethod
    def register_new_key() -> str:
        api_key = str(uuid4())
        db.execute(api_user_table.insert().values(api_key=api_key))
        return api_key

    @staticmethod
    def assign_user_roles(user_id: int, roles: Set[str]) -> None:
        if len(roles) == 0:
            return
        db.execute(delete(user_role_link_table).where(user_role_link_table.c.user_id == user_id))
        roles = db.execute(user_role_table.select().where(user_role_table.c.name.in_(roles))).fetchall()
        for role in roles:
            stmt = user_role_link_table.insert().values(user_id=user_id, role_id=role.id)
            db.execute(stmt)

    @staticmethod
    def insert_user(api_key: str, roles: Set[str], tracking: bool = True, registered: bool = False):
        insert_user_stmt = api_user_table.insert().values(api_key=api_key, tracking=tracking, registered=registered)
        db.execute(insert_user_stmt)
        u = APIUser.find_user(api_key=api_key)
        if len(roles) > 0:
            APIUser.assign_user_roles(u.id, roles)
        return u

    def delete_user(self) -> None:
        db.execute(delete(api_user_table).where(api_user_table.c.id == self.id))
        db.execute(delete(user_role_link_table).where(user_role_link_table.c.user_id == self.id))

    def update_user(self, api_key: str, roles: Set[str], tracking: bool = True, registered: bool = False) -> "APIUser":
        stmt = (
            update(api_user_table)
            .where(api_user_table.c.id == self.id)
            .values(api_key=api_key, tracking=tracking, registered=registered)
        )
        db.execute(stmt)
        APIUser.assign_user_roles(self.id, roles)
        self.api_key = api_key
        self.roles = roles
        self.tracking = tracking
        self.registered = registered
        return self

    @staticmethod
    def get_anonymous_user():
        anon_user = APIUser()
        anon_user.api_key = "anonymous"
        anon_user.authenticated = False
        return anon_user

    def has_role(self, required_role: str) -> bool:
        return required_role in [role for role in self.roles]

    def log_info(self, msg: str, *args, **kwargs) -> None:
        logger = get_structured_logger("api_key_logs", filename="api_keys_log.log")
        if self.authenticated:
            if self.tracking:
                logger.info(msg, *args, **dict(kwargs, api_key=self.api_key))
            else:
                logger.info(msg, *args, **dict(kwargs, apikey="*****"))
        else:
            logger.info(msg, *args, **kwargs)


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
        return auth_header[len("Bearer "):]
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


def _get_current_user():
    if "user" not in g:
        api_key = resolve_auth_token()
        user = APIUser.find_user(api_key=api_key)
        request_path = request.full_path
        if not user.authenticated and require_api_key():
            raise MissingAPIKeyException()
        # If the user configured no-track option, mask the API key
        if not user.tracking:
            request_path = mask_apikey(request_path)
        user.log_info("Get path", path=request_path)
        g.user = user
    return g.user


def get_api_user_id(api_key: str) -> int:
    stmt = api_user_table.select().where(api_user_table.c.api_key == api_key)
    user_id = db.execute(stmt).first().id
    return user_id


def show_soft_api_key_warning() -> bool:
    n = date.today()
    return not current_user.authenticated and not TESTING_MODE and API_KEY_SOFT_WARNING < n < API_KEY_HARD_WARNING


def show_hard_api_key_warning() -> bool:
    n = date.today()
    return not current_user.authenticated and n > API_KEY_HARD_WARNING and not TESTING_MODE


def register_user_role(role_name: str) -> None:
    try:
        db.execute(user_role_table.insert().values(name=role_name))
    except IntegrityError as e:
        app.logger.error(e)


current_user: APIUser = cast(APIUser, LocalProxy(_get_current_user))


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
    try:
        _get_current_user()
    except MissingAPIKeyException as e:
        raise e
    except:
        app.logger.error("User connection error", exc_info=True)
        if require_api_key():
            raise MissingAPIKeyException()
        else:
            g.user = APIUser.get_anonymous_user()


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


limiter = Limiter(app, key_func=_resolve_tracking_key, storage_uri=RATELIMIT_STORAGE_URL)


@limiter.request_filter
def _no_rate_limit() -> bool:
    if TESTING_MODE or _is_public_route():
        return False
    # no rate limit if user is registered
    user = _get_current_user()
    return user is not None and user.registered
