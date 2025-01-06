"""Storage folder."""

import uuid
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy import String, ForeignKey

from whathappened.database import Base
from whathappened.database.fields import GUID

from whathappened.models import UserProfile


class Folder(Base):
    """Data folder."""

    __tablename__ = "folder"
    id: Mapped[str] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    owner_id: Mapped[int] = mapped_column(ForeignKey("user_profile.id"), nullable=True)
    owner: Mapped[UserProfile] = relationship(
        backref=backref("folders", lazy="dynamic")
    )
    parent_id: Mapped[str] = mapped_column(
        GUID(), ForeignKey("folder.id"), default=None, nullable=True
    )
    subfolders: Mapped[list["Folder"]] = relationship(back_populates="parent")
    parent: Mapped["Folder"] = relationship(
        back_populates="subfolders", remote_side=[id]
    )
    title: Mapped[str] = mapped_column(String(128), nullable=True)
