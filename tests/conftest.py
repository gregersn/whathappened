from pathlib import Path

import pytest
from whathappened import create_app, assets
from whathappened.database import db as _db

from whathappened.config import Config

basedir = Path(__file__).parent.absolute()


class Conf(Config):
    TESTING = True
    TESTDB = basedir / 'testing.sqlite'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + str(TESTDB)
    WTF_CSRF_ENABLED = False


@pytest.fixture(scope='session')
def app(request):
    assets._named_bundles = {}
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
    if Conf.TESTDB.exists():
        Conf.TESTDB.unlink()

    def teardown():
        _db.drop_all()
        if Conf.TESTDB.exists():
            Conf.TESTDB.unlink()

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
