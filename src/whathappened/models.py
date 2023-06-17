from typing import cast
import uuid
import datetime
from sqlalchemy.orm import relationship
from sqlalchemy.sql.sqltypes import DateTime, Text
from sqlalchemy import Column, Integer, String, ForeignKey
from .database import Base
from .database.fields import GUID


class UserProfile(Base):
    __tablename__ = "user_profile"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user_account.id'))
    user = relationship("User", back_populates="profile")

    def __repr__(self):
        return f'<UserProfile {self.user_id}>'


class Invite(Base):
    __tablename__ = "invite"
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    owner_id = cast(int, Column(Integer, ForeignKey('user_profile.id')))
    table = Column(String(128))
    object_id = Column(Integer)

    def __init__(self, target: Base, **kwargs):
        super(Invite, self).__init__(**kwargs)
        self.table = target.__tablename__
        self.object_id = target.id

    @classmethod
    def query_for(cls, target: Base):
        return cls.query.filter_by(object_id=target.id) \
                        .filter_by(table=target.__tablename__)

    def matches(self, target: Base):
        return (target.__tablename__ == self.table and target.id == self.object_id)


class LogEntry(Base):
    __tablename__ = 'eventlog'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user_account.id'))
    table = Column(String(128))
    object_id = Column(Integer)
    entry = Column(Text)
    created_date = Column(DateTime, default=datetime.datetime.utcnow)
    user = relationship("User")

    def __init__(self, target: Base, entry: str, user_id=None, **kwargs):
        super(LogEntry, self).__init__(**kwargs)
        self.table = target.__tablename__
        self.object_id = target.id
        self.entry = entry
        if user_id is not None:
            self.user_id = user_id

    @classmethod
    def query_for(cls, target: Base):
        return cls.query.filter_by(object_id=target.id) \
                        .filter_by(table=target.__tablename__) \
                        .order_by(LogEntry.created_date.desc())
