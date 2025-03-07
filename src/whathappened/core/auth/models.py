"""Auth models."""

import logging

from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.sql.schema import ForeignKey
from sqlalchemy.sql.sqltypes import String
from werkzeug.security import check_password_hash, generate_password_hash

from whathappened.core.database import Base, session
from whathappened.core.database.models import UserProfile

logger = logging.getLogger(__name__)


class User(Base):
    """User account."""

    __tablename__ = "user_account"
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(
        String(64), index=True, unique=True, nullable=True
    )
    email: Mapped[str] = mapped_column(
        String(128), index=True, unique=True, nullable=True
    )
    password_hash: Mapped[str] = mapped_column(String(128), nullable=True)

    profile: Mapped[UserProfile] = relationship(
        "UserProfile", uselist=False, back_populates="user"
    )

    roles: Mapped[list["Role"]] = relationship(secondary="user_roles")

    def __repr__(self):
        return f"<User {self.username}>"

    def set_password(self, password: str):
        """Set user account password."""
        self.password_hash = generate_password_hash(password, "pbkdf2")

    def check_password(self, password: str):
        """Verify user account password."""
        return check_password_hash(str(self.password_hash), password)

    def has_role(self, role: str):
        """Check if user has role."""
        for r in self.roles:
            if r.name == role:
                return True
        return False

    __hash__ = object.__hash__

    @property
    def is_active(self):
        return True

    @property
    def is_authenticated(self):
        return self.is_active

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        try:
            return str(self.id)
        except AttributeError:
            raise NotImplementedError("No `id` attribute - override `get_id`") from None

    def __eq__(self, other):
        """
        Checks the equality of two `UserMixin` objects using `get_id`.
        """
        if isinstance(other, User):
            return self.get_id() == other.get_id()
        return NotImplemented

    def __ne__(self, other):
        """
        Checks the inequality of two `UserMixin` objects using `get_id`.
        """
        equal = self.__eq__(other)
        if equal is NotImplemented:
            return NotImplemented
        return not equal


class Role(Base):
    """Role a user can have."""

    __tablename__ = "roles"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=True)


class UserRoles(Base):
    """Connection between user and role."""

    __tablename__ = "user_roles"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("user_account.id", ondelete="CASCADE"), nullable=True
    )
    role_id: Mapped[int] = mapped_column(
        ForeignKey("roles.id", ondelete="CASCADE"), nullable=True
    )


def create_core_roles(*_, **__):
    """Create the core user roles."""
    session.add(Role(name="admin"))
    session.commit()


# This does not work after converting, but since the roles
# have not actually been in use, and are not created on
# other instances either, this should be looked over.
# TODO
# listen(Role.__table__, 'after_create', create_core_roles)


def add_first_admin(*_, **__):
    """Create the first user/admin."""
    session.add(UserRoles(user_id=1, role_id=1))
    session.commit()


# See above comment.
# listen(UserRoles.__table__, 'after_create', add_first_admin)
