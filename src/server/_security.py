from typing import Final, Set, cast
from enum import Enum
from flask import g
from werkzeug.local import LocalProxy
from ._common import app, request


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


def _get_current_user() -> User:
    if "user" not in g:
        # TODO
        g.user = ANONYMOUS_USER
    return g.user


"""
access to the SQL Alchemy connection for this request
"""
current_user: User = cast(User, LocalProxy(_get_current_user))


@app.before_request
def resolve_user():
    if request.path.startswith("/lib"):
        return
    # TODO