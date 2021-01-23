from app import db
import uuid
import datetime
from sqlalchemy.types import TypeDecorator, CHAR
from sqlalchemy.dialects.postgresql import UUID


class GUID(TypeDecorator):
    """Platform-independent GUID type.

    Uses PostgreSQL's UUID type, otherwise uses
    CHAR(32), storing as stringified hex values.

    """
    impl = CHAR

    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(UUID())
        else:
            return dialect.type_descriptor(CHAR(32))

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        elif dialect.name == 'postgresql':
            return str(value)
        else:
            if not isinstance(value, uuid.UUID):
                return "%.32x" % uuid.UUID(value).int
            else:
                # hexstring
                return "%.32x" % value.int

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        else:
            if not isinstance(value, uuid.UUID):
                value = uuid.UUID(value)
            return value


class UserProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user_account.id'))
    user = db.relationship("User", back_populates="profile")

    characters = db.relationship('Character', backref='player', lazy='dynamic')
    campaigns = db.relationship('Campaign', backref='owner', lazy='dynamic')

    def __repr__(self):
        return f'<UserProfile {self.user_id}>'


class Invite(db.Model):
    id = db.Column(GUID(), primary_key=True, default=uuid.uuid4)
    owner_id = db.Column(db.Integer, db.ForeignKey('user_profile.id'))
    table = db.Column(db.String(128))
    object_id = db.Column(db.Integer)

    def __init__(self, target: db.Model, **kwargs):
        super(Invite, self).__init__(**kwargs)
        self.table = target.__tablename__
        self.object_id = target.id

    @classmethod
    def query_for(cls, target: db.Model):
        return cls.query.filter_by(object_id=target.id) \
                        .filter_by(table=target.__tablename__)

    def matches(self, target: db.Model):
        return (target.__tablename__ == self.table
                and target.id == self.object_id)


class LogEntry(db.Model):
    __tablename__ = 'eventlog'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user_account.id'))
    table = db.Column(db.String(128))
    object_id = db.Column(db.Integer)
    entry = db.Column(db.Text)
    created_date = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    user = db.relationship("User")

    def __init__(self, target: db.Model, entry: str, user_id=None, **kwargs):
        super(LogEntry, self).__init__(**kwargs)
        self.table = target.__tablename__
        self.object_id = target.id
        self.entry = entry
        if user_id is not None:
            self.user_id = user_id

    @classmethod
    def query_for(cls, target: db.Model):
        return cls.query.filter_by(object_id=target.id) \
                        .filter_by(table=target.__tablename__) \
                        .order_by(LogEntry.created_date.desc())
