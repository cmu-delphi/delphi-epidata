from typing import Set, Optional, List, Dict, cast
from datetime import datetime, timedelta, date
from uuid import uuid4
import re
from functools import wraps

from sqlalchemy import ForeignKey, Column, Integer, String, Boolean, DateTime, delete, update
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

from werkzeug.local import LocalProxy

from flask import g, Response
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from ._db import engine
from ._config import API_KEY_EXPIRE_AFTER, API_KEY_REQUIRED_STARTING_AT, URL_PREFIX, RATELIMIT_STORAGE_URL
from ._common import request, app
from ._exceptions import MissingAPIKeyException, UnAuthenticatedException
from ._logger import get_structured_logger


Base = declarative_base()
Session = sessionmaker(bind=engine)
session = Session()

DTIME_NOW = datetime.now()
DATE_TODAY = date.today()

API_KEY_HARD_WARNING = API_KEY_REQUIRED_STARTING_AT - timedelta(days=14)
API_KEY_SOFT_WARNING = API_KEY_HARD_WARNING - timedelta(days=14)

API_KEY_WARNING_TEXT = (
    "an api key will be required starting at {}, go to https://delphi.cmu.edu to request one".format(
        API_KEY_REQUIRED_STARTING_AT
    )
)

TESTING_MODE = app.config.get("TESTING", False)


class User(Base):
    __tablename__ = "api_user"

    id = Column(Integer, primary_key=True, autoincrement=True)
    api_key = Column(String(50), unique=True)
    roles = relationship("UserRole", secondary="user_role_link", cascade="all, delete")
    tracking = Column(Boolean, default=True)
    registered = Column(Boolean, default=False)
    creation_date = Column(DateTime)
    expiration_date = Column(DateTime)
    last_api_access_date = Column(DateTime)


class UserRole(Base):
    __tablename__ = "user_role"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), unique=True)


class UserRoleLink(Base):
    __tablename__ = "user_role_link"

    user_id = Column(Integer, ForeignKey("api_user.id", ondelete="CASCADE"), primary_key=True)
    role_id = Column(Integer, ForeignKey("user_role.id", ondelete="CASCADE"), primary_key=True)


Base.metadata.create_all(engine)


def create_user_role(role_name: str) -> None:
    user_role = UserRole(name=role_name)
    session.add(user_role)
    session.commit()

class AbstractUser:
    id: int
    api_key: str
    roles: Set[str] = set()
    tracking: bool = True
    registered: bool = False
    creation_date: datetime = DTIME_NOW
    expiration_date: datetime = DTIME_NOW + timedelta(days=API_KEY_EXPIRE_AFTER)
    last_api_access_date: datetime = DTIME_NOW

    @staticmethod
    def find_user(user_id: Optional[int] = None, api_key: Optional[str] = None):
        user = None
        if user_id is not None:
            user = session.query(User).filter(User.id == user_id).first()
        if api_key is not None:
            user = session.query(User).filter(User.api_key == api_key).first()
        if user is None:
            return None
        return user


class DBUser(AbstractUser):
    @property
    def roles_str(self):
        return "\n".join(self.roles)

    @staticmethod
    def roles_to_assign(roles: Set[str]):
        return session.query(UserRole).filter(UserRole.name.in_(roles)).all()

    @staticmethod
    def assign_new_roles(roles: Set[str], user_id: int):
        user = session.query(User).filter(User.id == user_id).first()
        roles_to_assign = DBUser.roles_to_assign(roles)
        user.roles = []
        user.roles.extend(roles_to_assign)
        session.commit()
        return user

    @staticmethod
    def _parse(r: Dict) -> "DBUser":
        user_roles = session.query(User).filter(User.id == r["id"]).first().roles
        u = DBUser()
        u.id = r["id"]
        u.api_key = r["api_key"]
        u.roles = set(role.name for role in user_roles)
        u.tracking = r["tracking"] != False
        u.registered = r["registered"] == True
        u.creation_date = r["creation_date"]
        u.expiration_date = r["expiration_date"]
        u.last_api_access_date = r["last_api_access_date"]
        return u

    @staticmethod
    def find_user(user_id: Optional[int] = None, api_key: Optional[str] = None) -> Optional["DBUser"]:
        user = AbstractUser.find_user(user_id, api_key)
        if user is None:
            return None
        return DBUser._parse(user.__dict__)

    @staticmethod
    def list() -> List["DBUser"]:
        return [DBUser._parse(u.__dict__) for u in session.query(User).all()]

    @staticmethod
    def insert(
        api_key: str,
        roles: Set[str] = set(),
        tracking: bool = True,
        registered: bool = False,
        creation_date: datetime = DTIME_NOW,
        expiration_date: datetime = DTIME_NOW + timedelta(days=API_KEY_EXPIRE_AFTER),
        last_api_access_date: datetime = DTIME_NOW,
    ):
        new_user = User(
            api_key=api_key,
            tracking=tracking,
            registered=registered,
            creation_date=creation_date,
            expiration_date=expiration_date,
            last_api_access_date=last_api_access_date,
        )
        session.add(new_user)
        session.commit()
        DBUser.assign_new_roles(roles, new_user.id)

    @staticmethod
    def register_new_key() -> str:
        api_key = str(uuid4())
        DBUser.insert(api_key)
        return api_key

    def delete_user(self):
        stmt = delete(User).filter(User.id == self.id).execution_options(synchronize_session="fetch")
        session.execute(stmt)
        session.commit()

    def update_user(self, api_key: str, roles: Set[str], tracking: bool = True, registered: bool = False) -> "DBUser":
        stmt = (
            update(User)
            .where(User.id == self.id)
            .values(api_key=api_key, tracking=tracking, registered=registered)
            .execution_options(synchronize_session="fetch")
        )
        session.execute(stmt)
        session.commit()
        DBUser.assign_new_roles(roles, self.id)
        self.api_key = api_key
        self.tracking = tracking
        self.registered = registered
        self.roles = roles
        return self

    def update_last_api_access_date(self) -> None:
        dtime_now = datetime.now()
        stmt = (
            update(User)
            .where(User.id == self.id)
            .values(last_api_access_date=dtime_now)
            .execution_options(synchronize_session="fetch")
        )
        session.execute(stmt)
        session.commit()
        self.last_api_access_date = dtime_now


class APIUser(AbstractUser):
    def __init__(
        self,
        api_key: str,
        authenticated: bool,
        roles: Set[str],
        tracking: bool = True,
        registered: bool = False,
        creation_date: datetime = DTIME_NOW,
        expiration_date: datetime = DTIME_NOW + timedelta(days=API_KEY_EXPIRE_AFTER),
        last_api_access_date: datetime = DTIME_NOW,
    ) -> None:
        self.api_key = api_key
        self.authenticated = authenticated
        self.roles = roles
        self.tracking = tracking
        self.registered = registered
        self.creation_date = creation_date
        self.expiration_date = expiration_date
        self.last_api_access_date = last_api_access_date

    @staticmethod
    def get_anonymous_user():
        return APIUser("anonymous", False, set())

    
    def has_role(self, required_role: str) -> bool:
        return required_role in [role for role in self.roles]
    
    @staticmethod
    def find_user(user_id: Optional[int] = None, api_key: Optional[str] = None) -> "APIUser":
        user = AbstractUser.find_user(user_id, api_key)
        if user is None:
            return APIUser.get_anonymous_user()
        return APIUser(
            api_key=user.api_key,
            authenticated=True,
            roles=set([role.name for role in user.roles]),
            tracking=user.tracking,
            registered=user.registered,
            creation_date=user.creation_date,
            expiration_date=user.expiration_date,
            last_api_access_date=user.last_api_access_date,
        )

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
    return DATE_TODAY >= API_KEY_REQUIRED_STARTING_AT and not TESTING_MODE


def _get_current_user() -> APIUser:
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


current_user: APIUser = cast(APIUser, LocalProxy(_get_current_user))


def show_soft_api_key_warning() -> bool:
    return (
        not current_user.authenticated
        and not TESTING_MODE
        and DATE_TODAY > API_KEY_SOFT_WARNING
        and DATE_TODAY < API_KEY_HARD_WARNING
    )


def show_hard_api_key_warning() -> bool:
    return not current_user.authenticated and DATE_TODAY > API_KEY_HARD_WARNING and not TESTING_MODE


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
        dbuser = DBUser().find_user(api_key=g.user.api_key)
        dbuser.update_last_api_access_date()
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
