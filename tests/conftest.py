from pathlib import Path
from fastapi import FastAPI
from fastapi.testclient import TestClient
import pytest
from whathappened.database.base import db as _db

from whathappened.config import Settings

basedir = Path(__file__).parent.absolute()


class Conf(Settings):
    TESTING: bool = True
    TESTDB: Path = basedir / 'testing.sqlite'
    SQLALCHEMY_DATABASE_URI: str = 'sqlite:///' + str(TESTDB)
    WTF_CSRF_ENABLED: bool = False


Config = Conf()


@pytest.fixture(scope='session')
def app(request):
    app = FastAPI(title="Test app")

    return app


@pytest.fixture(scope='session')
def db(app, request):
    """Session-wide test database."""
    if Config.TESTDB.exists():
        Config.TESTDB.unlink()

    def teardown():
        _db.drop_all()
        if Config.TESTDB.exists():
            Config.TESTDB.unlink()

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
    client = TestClient(app)
    return client


class AuthActions(object):

    def __init__(self, client):
        self._client = client

    def login(self, username='test', password='test'):
        return self._client.post('/auth/login', data={'username': username, 'password': password})

    def logout(self):
        return self._client.get('/auth/logout')


@pytest.fixture
def auth(client):
    return AuthActions(client)
