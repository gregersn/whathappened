from app import db
import uuid
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
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship("User", back_populates="profile")

    characters = db.relationship('Character', backref='player', lazy='dynamic')

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
