from typing import Final, Optional, Set, cast
from enum import Enum
from functools import wraps
from flask import g
from werkzeug.local import LocalProxy
from sqlalchemy import Table, Column, String, Integer, JSON
from ._common import app, request, db
from ._exceptions import MissingAPIKeyException
from ._db import metadata, TABLE_OPTIONS

user_table = Table(
    "api_user",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("api_key", String(50)),
    Column("email", String(100)),
    Column("roles", JSON()),
    **TABLE_OPTIONS,
)


class UserRole(str, Enum):
    afhsb = "afhsb"
    cdc = "cdc"
    fluview = "fluview"
    ght = "ght"
    norostat = "norostat"
    quidel = "quidel"
    sensors = "sensors"
    sensor_twtr = "sensor_twtr"
    sensor_gft = "sensor_gft"
    sensor_ght = "sensor_ght"
    sensor_ghtj = "sensor_ghtj"
    sensor_cdc = "sensor_cdc"
    sensor_quid = "sensor_quid"
    sensor_wiki = "sensor_wiki"
    twitter = "twitter"


# begin sensor query authentication configuration
#   A multimap of sensor names to the "granular" auth tokens that can be used to access them; excludes the "global" sensor auth key that works for all sensors:
GRANULAR_SENSOR_ROLES = {
    "twtr": UserRole.sensor_twtr,
    "gft": UserRole.sensor_gft,
    "ght": UserRole.sensor_ght,
    "ghtj": UserRole.sensor_ghtj,
    "cdc": UserRole.sensor_cdc,
    "quid": UserRole.sensor_quid,
    "wiki": UserRole.sensor_wiki,
}

#   A set of sensors that do not require an auth key to access:
OPEN_SENSORS = [
    "sar3",
    "epic",
    "arch",
]


class User:
    user_id: Final[str]
    roles: Final[Set[UserRole]]
    authenticated: Final[bool]

    def __init__(self, user_id: str, authenticated: bool, roles: Set[UserRole]) -> None:
        self.user_id = user_id
        self.authenticated = authenticated
        self.roles = roles

    def has_role(self, role: UserRole) -> bool:
        return role in self.roles


ANONYMOUS_USER = User("anonymous", False, set())


def resolve_auth_token() -> Optional[str]:
    # auth request param
    if "auth" in request.values:
        return request.values["auth"]
    if "api_key" in request.values:
        return request.values["api_key"]
    # user name password
    if request.authorization and request.authorization.username == "epidata":
        return request.authorization.password
    # bearer token authentication
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        return auth_header[len("Bearer ") :]
    return None


def _get_current_user() -> User:
    if "user" not in g:
        api_key = resolve_auth_token()
        if not api_key:
            raise MissingAPIKeyException()
        stmt = user_table.select().where(user_table.c.api_key == api_key)
        user = db.execution_options(stream_results=False).execute(stmt).first()
        if user is None:
            raise MissingAPIKeyException()
        g.user = User(str(user.id), True, set(user.roles or []))
    return g.user


"""
access to the SQL Alchemy connection for this request
"""
current_user: User = cast(User, LocalProxy(_get_current_user))


@app.before_request
def resolve_user():
    if request.path.startswith("/lib"):
        return
    _get_current_user()


def require_role(required_role: Optional[UserRole]):
    def decorator_wrapper(f):
        if not required_role:
            return f

        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user or not current_user.has_role(required_role):
                raise MissingAPIKeyException()
            return f(*args, **kwargs)

        return decorated_function

    return decorator_wrapper