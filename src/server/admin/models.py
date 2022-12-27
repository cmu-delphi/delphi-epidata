
from sqlalchemy import Table, ForeignKey, Column, Integer, String, Boolean, delete, update
from sqlalchemy.orm import relationship
from .._db import Base, session
from typing import Set, Optional, List

association_table = Table(
    "user_role_link",
    Base.metadata,
    Column("user_id", ForeignKey("api_user.id")),
    Column("role_id", ForeignKey("user_role.id")),
)


class User(Base):
    __tablename__ = "api_user"
    id = Column(Integer, primary_key=True, autoincrement=True)
    roles = relationship("UserRole", secondary=association_table)
    api_key = Column(String(50), unique=True)
    tracking = Column(Boolean, default=True)
    registered = Column(Boolean, default=False)

    def __init__(self, api_key: str, tracking: bool = True, registered: bool = False) -> None:
        self.api_key = api_key
        self.tracking = tracking
        self.registered = registered

    @staticmethod
    def list_users() -> List["User"]:
        return session.query(User).all()

    @property
    def is_authenticated(self):
        return True if self.api_key != "anonymous" else False

    @property
    def as_dict(self):
        fields_list = ["id", "api_key", "tracking", "registered", "roles"]
        user_dict = self.__dict__
        user_dict["roles"] = self.get_user_roles
        return {k: v for k, v in user_dict.items() if k in fields_list}

    @property
    def get_user_roles(self) -> Set[str]:
        return set([role.name for role in self.roles])

    def has_role(self, required_role: str) -> bool:
        return required_role in self.get_user_roles

    @staticmethod
    def assign_roles(user: "User", roles: Optional[Set[str]]) -> None:
        if roles:
            roles_to_assign = session.query(UserRole).filter(UserRole.name.in_(roles)).all()
            user.roles = roles_to_assign
            session.commit()
        else:
            user.roles = []
            session.commit()

    @staticmethod
    def find_user(user_id: Optional[int] = None, api_key: Optional[str] = None) -> "User":
        user = session.query(User).filter((User.id == user_id) | (User.api_key == api_key)).first()
        return user if user else User("anonymous")

    @staticmethod
    def create_user(api_key: str, user_roles: Optional[Set[str]] = None, tracking: bool = True, registered: bool = False) -> "User":
        new_user = User(api_key=api_key, tracking=tracking, registered=registered)
        session.add(new_user)
        session.commit()
        User.assign_roles(new_user, user_roles)
        return new_user

    @staticmethod
    def update_user(user: "User", api_key: Optional[str], roles: Optional[Set[str]], tracking: Optional[bool], registered: Optional[bool]) -> "User":
        user = User.find_user(user_id=user.id)
        if user:
            update_stmt = update(User).where(User.id == user.id).values(api_key=api_key, tracking=tracking, registered=registered)
            session.execute(update_stmt)
            session.commit()
            User.assign_roles(user, roles)
        return user

    @staticmethod
    def delete_user(user_id: int) -> None:
        session.execute(delete(User).where(User.id == user_id))
        session.commit()


class UserRole(Base):
    __tablename__ = "user_role"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), unique=True)

    @staticmethod
    def create_role(name: str) -> None:
        session.execute(f"""
        INSERT INTO user_role (name)
        SELECT '{name}'
        WHERE NOT EXISTS
            (SELECT *
            FROM user_role
            WHERE name='{name}')
        """)
        session.commit()

    @staticmethod
    def list_all_roles():
        roles = session.query(UserRole).all()
        return [role.name for role in roles]
