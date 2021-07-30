import logging
from time import time
import jwt
from flask_login import UserMixin
from flask import current_app
from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import Column, ForeignKey
from sqlalchemy.sql.sqltypes import Integer, String
from werkzeug.security import check_password_hash, generate_password_hash

from whathappened.database import Base, session

logger = logging.getLogger(__name__)


class User(UserMixin, Base):
    __tablename__ = "user_account"
    id = Column(Integer, primary_key=True)
    username = Column(String(64), index=True, unique=True)
    email = Column(String(128), index=True, unique=True)
    password_hash = Column(String(128))

    profile = relationship('UserProfile', uselist=False,
                           back_populates="user")

    roles = relationship('Role', secondary='user_roles')

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password: str):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str):
        return check_password_hash(self.password_hash, password)

    def get_reset_password_token(self, expires_in: int = 600):
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            current_app.config['SECRET_KEY'], algorithm='HS256') \
            .decode('utf-8')

    @staticmethod
    def verify_reset_password_token(token: str):
        try:
            id = jwt.decode(token, current_app.config['SECRET_KEY'],
                            algorithms=['HS256'])['reset_password']
        except Exception:
            logger.error("Exception occurent while trying to reset password.",
                         exc_info=True)
            return
        return User.query.get(id)

    def has_role(self, role: str):
        for r in self.roles:
            if r.name == role:
                return True
        return False


class Role(Base):
    __tablename__ = 'roles'
    id = Column(Integer(), primary_key=True)
    name = Column(String(50), unique=True)


class UserRoles(Base):
    __tablename__ = 'user_roles'
    id = Column(Integer(), primary_key=True)
    user_id = Column(Integer(),
                     ForeignKey('user_account.id', ondelete='CASCADE'))
    role_id = Column(Integer(),
                     ForeignKey('roles.id', ondelete='CASCADE'))


def create_core_roles(*args, **kwargs):
    session.add(Role(name='admin'))
    session.commit()


# This does not work after converting, but since the roles
# have not actually been in use, and are not created on
# other instances either, this should be looked over.
# TODO
# listen(Role.__table__, 'after_create', create_core_roles)


def add_first_admin(*args, **kwargs):
    session.add(UserRoles(user_id=1, role_id=1))
    session.commit()

# See above comment.
# listen(UserRoles.__table__, 'after_create', add_first_admin)
