from pathlib import Path
from typing import get_type_hints, Any
import warnings
from flask import Flask
import typeguard

import pytest
from sqlalchemy import NullPool, create_engine
from whathappened.web import create_app
from whathappened.web.main import assets
from whathappened.core.database import db as _db

from whathappened.config import Settings
from whathappened.core.database.base import Base, Session

basedir = Path(__file__).parent.absolute()


def pytest_runtest_call(item: pytest.Function) -> None:
    """Check test typing.

    Copied from: https://github.com/pytest-dev/pytest/issues/5981#issuecomment-1875730079
    """
    try:
        annotations = get_type_hints(
            item.obj,
            globalns=item.obj.__globals__,
            localns={"Any": Any},  # pytest-bdd appears to insert an `Any` annotation
        )
    except TypeError:
        # get_type_hints may fail on Python <3.10 because pytest-bdd appears to have
        # `dict[str, str]` as a type somewhere, and builtin type subscripting isn't
        # supported yet
        warnings.warn(
            f"Type annotations could not be retrieved for {item.obj!r}", RuntimeWarning
        )
        return

    for attr, type_ in annotations.items():
        if attr in item.funcargs:
            typeguard.check_type(item.funcargs[attr], type_)


class Conf(Settings):
    TESTING: bool = True
    TESTDB: Path = basedir / "testing.sqlite"
    SQLALCHEMY_DATABASE_URI: str = "sqlite:///" + str(TESTDB)
    WTF_CSRF_ENABLED: bool = False


Config = Conf()


@pytest.fixture(scope="session")
def test_app(request):
    assets._named_bundles = {}
    test_app = create_app(Config)

    ctx = test_app.app_context()
    ctx.push()

    def teardown():
        ctx.pop()

    request.addfinalizer(teardown)

    return test_app


@pytest.fixture(scope="session")
def db(test_app: Flask, request):
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
def client(test_app, request):
    client = test_app.test_client()
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
