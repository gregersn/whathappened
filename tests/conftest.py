import os
import tempfile

import pytest
from app import create_app, db as _db

from config import Config

class Conf(Config):
    TESTING = True
    TESTDB = "./whathappened.sqlite"
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + TESTDB
    WTF_CSRF_ENABLED = False


@pytest.fixture(scope='session')
def app(request):
    app = create_app(Conf)

    ctx = app.app_context()
    ctx.push()

    def teardown():
        ctx.pop()
    
    request.addfinalizer(teardown)

    return app


@pytest.fixture(scope='session')
def db(app, request):
    """Session-wide test database."""
    if os.path.exists(Conf.TESTDB):
        os.unlink(Conf.TESTDB)

    def teardown():
        _db.drop_all()
        if os.path.isfile(Conf.TESTDB):
            os.unlink(Conf.TESTDB)

    _db.app = app
    _db.create_all()

    request.addfinalizer(teardown)
    return _db


@pytest.fixture(scope='function')
def session(db, request):
    """Creates a new database session for a test."""
    connection = db.engine.connect()
    transaction = connection.begin()

    options = dict(bind=connection, binds={})
    session = db.create_scoped_session(options=options)

    db.session = session

    def teardown():
        transaction.rollback()
        connection.close()
        session.remove()

    request.addfinalizer(teardown)
    return session

@pytest.fixture(scope='function')
def client(app, request):
    client = app.test_client()
    return client


class AuthActions(object):
    def __init__(self, client):
        self._client = client

    def login(self, username='test', password='test'):
        return self._client.post(
            '/auth/login',
            data={'username': username, 'password': password}
        )

    def logout(self):
        return self._client.get('/auth/logout')


@pytest.fixture
def auth(client):
    return AuthActions(client)
