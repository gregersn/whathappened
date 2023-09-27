import uuid
from sqlalchemy.orm import relationship, backref
from sqlalchemy import Column, Integer, String, ForeignKey

from whathappened.database import Base
from whathappened.database.fields import GUID


class Folder(Base):
    __tablename__ = "folder"
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    owner_id = Column(Integer, ForeignKey("user_profile.id"))
    owner = relationship("UserProfile", backref=backref("folders", lazy="dynamic"))
    parent_id = Column(GUID(), ForeignKey("folder.id"), default=None, nullable=True)

    subfolders = relationship("Folder", backref=backref("parent", remote_side=[id]))
    title = Column(String(128))
