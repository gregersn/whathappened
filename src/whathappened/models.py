"""User handling models."""

import typing
import uuid
import datetime
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.sql.sqltypes import DateTime, Text
from sqlalchemy import String, ForeignKey

from whathappened.database import Base
from whathappened.database.fields import GUID

if typing.TYPE_CHECKING:
    from whathappened.auth.models import User


class UserProfile(Base):
    """User information."""

    __tablename__ = "user_profile"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user_account.id"), nullable=True)
    user: Mapped["User"] = relationship(back_populates="profile")

    def __repr__(self):
        return f"<UserProfile {self.user_id}>"


class Invite(Base):
    """User invite."""

    __tablename__ = "invite"
    id: Mapped[str] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    owner_id: Mapped[int] = mapped_column(ForeignKey("user_profile.id"), nullable=True)
    table: Mapped[str] = mapped_column(String(128), nullable=True)
    object_id: Mapped[int] = mapped_column(nullable=True)

    def __init__(self, target: typing.Any, **kwargs):
        super().__init__(**kwargs)
        self.table = target.__tablename__
        self.object_id = target.id

    @classmethod
    def query_for(cls, target: typing.Any):
        """Find invites by target."""
        return cls.query.filter_by(object_id=target.id).filter_by(
            table=target.__tablename__
        )

    def matches(self, target: typing.Any):
        """Find invite matches."""
        return target.__tablename__ == self.table and target.id == self.object_id


class LogEntry(Base):
    """Entry in changelog."""

    __tablename__ = "eventlog"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user_account.id"), nullable=True)
    table: Mapped[str] = mapped_column(String(128), nullable=True)
    object_id: Mapped[int] = mapped_column(nullable=True)
    entry: Mapped[str] = mapped_column(Text, nullable=True)
    created_date = mapped_column(DateTime, default=datetime.datetime.utcnow)
    user: Mapped["User"] = relationship()

    def __init__(self, target: typing.Any, entry: str, user_id=None, **kwargs):
        super().__init__(**kwargs)
        self.table = target.__tablename__
        self.object_id = target.id
        self.entry = entry
        if user_id is not None:
            self.user_id = user_id

    @classmethod
    def query_for(cls, target: typing.Any):
        """Look up logentries by object."""
        return (
            cls.query.filter_by(object_id=target.id)
            .filter_by(table=target.__tablename__)
            .order_by(LogEntry.created_date.desc())
        )
