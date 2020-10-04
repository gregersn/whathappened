import logging
from time import time
import jwt
from flask_login import UserMixin
from flask import current_app
from werkzeug.security import check_password_hash, generate_password_hash

from sqlalchemy.event import listen

from app import db

logger = logging.getLogger(__name__)


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(128), index=True, unique=True)
    password_hash = db.Column(db.String(128))

    profile = db.relationship('UserProfile', uselist=False,
                              back_populates="user")

    roles = db.relationship('Role', secondary='user_roles')

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            current_app.config['SECRET_KEY'], algorithm='HS256') \
                       .decode('utf-8')

    @staticmethod
    def verify_reset_password_token(token):
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


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(50), unique=True)


class UserRoles(db.Model):
    __tablename__ = 'user_roles'
    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer(),
                        db.ForeignKey('user.id', ondelete='CASCADE'))
    role_id = db.Column(db.Integer(),
                        db.ForeignKey('roles.id', ondelete='CASCADE'))


def create_core_roles(*args, **kwargs):
    db.session.add(Role(name='admin'))
    db.session.commit()


listen(Role.__table__, 'after_create', create_core_roles)


def add_first_admin(*args, **kwargs):
    db.session.add(UserRoles(user_id=1, role_id=1))
    db.session.commit()


listen(UserRoles.__table__, 'after_create', add_first_admin)
