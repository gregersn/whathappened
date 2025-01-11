from pathlib import Path

import pytest
from sqlalchemy import NullPool, create_engine
from whathappened import create_app, assets
from whathappened.core.database import db as _db

from whathappened.config import Settings
from whathappened.core.database.base import Base, Session

basedir = Path(__file__).parent.absolute()


class Conf(Settings):
    TESTING: bool = True
    TESTDB: Path = basedir / "testing.sqlite"
    SQLALCHEMY_DATABASE_URI: str = "sqlite:///" + str(TESTDB)
    WTF_CSRF_ENABLED: bool = False


Config = Conf()


@pytest.fixture(scope="session")
def app(request):
    assets._named_bundles = {}
    app = create_app(Config)

    ctx = app.app_context()
    ctx.push()

    def teardown():
        ctx.pop()

    request.addfinalizer(teardown)

    return app


@pytest.fixture(scope="session")
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


@pytest.fixture(scope="function")
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


@pytest.fixture(scope="function")
def client(app, request):
    client = app.test_client()
    return client


class AuthActions:
    def __init__(self, client):
        self._client = client

    def login(self, username="test", password="test"):
        return self._client.post(
            "/auth/login", data={"username": username, "password": password}
        )

    def logout(self):
        return self._client.get("/auth/logout")


@pytest.fixture
def auth(client):
    return AuthActions(client)


@pytest.fixture(scope="session")
def connection(request):
    engine = create_engine(
        "sqlite:///test_db_2.sqlite", poolclass=NullPool, future=True
    )
    connection = engine.connect()

    def teardown():
        print("TEARDOWN")

    request.addfinalizer(teardown)
    return connection


@pytest.fixture(scope="session", autouse=True)
def setup_db(connection, request):
    Base.metadata.create_all(bind=connection)

    def teardown():
        Base.metadata.drop_all(bind=connection)

    request.addfinalizer(teardown)


@pytest.fixture(autouse=True)
def new_session(connection, request):
    # transaction = connection.begin()
    session = Session(bind=connection)
    session.begin_nested()

    # @event.listens_for(session, "after_transaction_end")
    def restart_savepoint(db_session, transaction):
        raise NotImplementedError

    def teardown():
        # Session.remove()
        # transaction.rollback()
        ...

    request.addfinalizer(teardown)
    return session
