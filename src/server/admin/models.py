from sqlalchemy import Table, ForeignKey, Column, Integer, String, Date, delete, update
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from copy import deepcopy

from .._db import Session, WriteSession, default_session
from delphi.epidata.common.logger import get_structured_logger

from typing import Set, Optional
from datetime import date


Base = declarative_base()

association_table = Table(
    "user_role_link",
    Base.metadata,
    Column("user_id", ForeignKey("api_user.id")),
    Column("role_id", ForeignKey("user_role.id")),
)

def _default_date_now():
    return date.today()

class User(Base):
    __tablename__ = "api_user"
    id = Column(Integer, primary_key=True, autoincrement=True)
    roles = relationship("UserRole", secondary=association_table, lazy="joined") # last arg does an eager load of this property from foreign tables
    api_key = Column(String(50), unique=True, nullable=False)
    email = Column(String(320), unique=True, nullable=False)
    created = Column(Date, default=_default_date_now)
    last_time_used = Column(Date, default=_default_date_now)

    def __init__(self, api_key: str, email: str = None) -> None:
        self.api_key = api_key
        self.email = email


    def has_role(self, required_role: str) -> bool:
        return required_role in set(role.name for role in self.roles)

    @staticmethod
    def _assign_roles(user: "User", roles: Optional[Set[str]], session) -> None:
        get_structured_logger("api_user_models").info("setting roles", roles=roles, user_id=user.id, api_key=user.api_key)
        db_user = session.query(User).filter(User.id == user.id).first()
        # TODO: would it be sufficient to use the passed-in `user` instead of looking up this `db_user`?
        #       or even use this as a bound method instead of a static??
        #       same goes for `update_user()` and `delete_user()` below...
        if roles:
            db_user.roles = session.query(UserRole).filter(UserRole.name.in_(roles)).all()
        else:
            db_user.roles = []
        session.commit()
        # retrieve the newly updated User object
        return session.query(User).filter(User.id == user.id).first()

    @staticmethod
    @default_session(Session)
    def find_user(*, # asterisk forces explicit naming of all arguments when calling this method
                  session,
                  user_id: Optional[int] = None, api_key: Optional[str] = None, user_email: Optional[str] = None
    ) -> "User":
        # NOTE: be careful, using multiple arguments could match multiple users, but this will return only one!
        user = (
            session.query(User)
            .filter((User.id == user_id) | (User.api_key == api_key) | (User.email == user_email))
            .first()
        )
        return user if user else None

    @staticmethod
    @default_session(WriteSession)
    def create_user(api_key: str, email: str, session, user_roles: Optional[Set[str]] = None) -> "User":
        get_structured_logger("api_user_models").info("creating user", api_key=api_key)
        new_user = User(api_key=api_key, email=email)
        session.add(new_user)
        session.commit()
        return User._assign_roles(new_user, user_roles, session)

    @staticmethod
    @default_session(WriteSession)
    def update_user(
        user: "User",
        email: Optional[str],
        api_key: Optional[str],
        roles: Optional[Set[str]],
        session
    ) -> "User":
        get_structured_logger("api_user_models").info("updating user", user_id=user.id, new_api_key=api_key)
        user = User.find_user(user_id=user.id, session=session)
        if not user:
            raise Exception('user not found')
        update_stmt = (
            update(User)
            .where(User.id == user.id)
            .values(api_key=api_key, email=email)
        )
        session.execute(update_stmt)
        return User._assign_roles(user, roles, session)

    @staticmethod
    @default_session(WriteSession)
    def delete_user(user_id: int, session) -> None:
        get_structured_logger("api_user_models").info("deleting user", user_id=user_id)
        session.execute(delete(User).where(User.id == user_id))
        session.commit()


class UserRole(Base):
    __tablename__ = "user_role"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), unique=True)

    def __repr__(self):
        return self.name

    @staticmethod
    @default_session(WriteSession)
    def create_role(name: str, session) -> None:
        get_structured_logger("api_user_models").info("creating user role", role=name)
        # TODO: check role doesnt already exist
        session.execute(f"""
            INSERT INTO user_role (name)
            SELECT '{name}'
            WHERE NOT EXISTS
                (SELECT *
                FROM user_role
                WHERE name='{name}')
        """)
        session.commit()
        return session.query(UserRole).filter(UserRole.name == name).first()

    @staticmethod
    @default_session(Session)
    def list_all_roles(session):
        roles = session.query(UserRole).all()
        return [role.name for role in roles]


class RegistrationResponse(Base):
    __tablename__ = "registration_responses"

    email = Column(String(320), unique=True, nullable=False, primary_key=True)
    organization = Column(String(120), unique=False, nullable=True)
    purpose = Column(String(320), unique=False, nullable=True)

    def __init__(self, email: str, organization: str = None, purpose: str = None) -> None:
        self.email = email
        self.organization = organization
        self.purpose = purpose

    @staticmethod
    @default_session(WriteSession)
    def add_response(email: str, organization: str, purpose: str, session):
        new_response = RegistrationResponse(email, organization, purpose)
        session.add(new_response)
        session.commit()


class RemovalRequest(Base):
    __tablename__ = "removal_requests"

    api_key = Column(String(50), unique=True, nullable=False, primary_key=True)
    comment = Column(String(320), unique=False, nullable=True)

    def __init__(self, api_key: str, comment: str = None) -> None:
        self.api_key = api_key
        self.comment = comment

    @staticmethod
    @default_session(WriteSession)
    def add_request(api_key: str, comment: str, session):
        new_request = RemovalRequest(api_key, comment)
        session.add(new_request)
        session.commit()