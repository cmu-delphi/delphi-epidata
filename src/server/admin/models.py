from sqlalchemy import Table, ForeignKey, Column, Integer, String, Date, delete, update
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from copy import deepcopy

from .._db import Session, WriteSession, default_session
from delphi_utils import get_structured_logger

from typing import Set, Optional, List
from datetime import datetime as dtime


Base = declarative_base()

association_table = Table(
    "user_role_link",
    Base.metadata,
    Column("user_id", ForeignKey("api_user.id")),
    Column("role_id", ForeignKey("user_role.id")),
)

def _default_date_now():
    return dtime.strftime(dtime.now(), "%Y-%m-%d")

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

    @property
    def as_dict(self):
        return {
            "id": self.id,
            "api_key": self.api_key,
            "email": self.email,
            "roles": set(role.name for role in self.roles),
            "created": self.created,
            "last_time_used": self.last_time_used
        }

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
