import pytest
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql.sqltypes import String
from whathappened.auth.models import User
from whathappened.core.database import init_db, db
from whathappened.core.database.base import Base, BaseModel
from whathappened.core.database.pagination import paginate
from whathappened.models import LogEntry


class DataModel(Base):
    __tablename__ = "test_table"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(256))


def test_connect_db():
    db_uri = "sqlite:///whathappened_test_db.sqlite"
    init_db(db_uri, nullpool=True)
    db.drop_all()
    db.create_all()

    tests = DataModel.query.all()
    assert len(tests) == 0

    test = DataModel(title="test object")
    db.session.add(test)
    db.session.commit()

    tests = DataModel.query.all()
    assert len(tests) == 1


class SerializeModel(BaseModel):
    __tablename__ = "test_table_2"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(256))
    action: Mapped[str] = mapped_column(String(256))

    _default_fields = ["id", "title", "action"]


def test_serialize():
    data = {"id": None, "title": "test object", "action": "do it"}

    test = SerializeModel()

    ser = test.to_dict()
    assert ser != data

    test.from_dict(**data)

    ser = test.to_dict()

    assert ser == data


def test_paginate(db):
    log_user = User(username="testuser")
    db.session.add(log_user)
    db.session.commit()
    for i in range(40):
        log_entry = LogEntry(log_user, f"entry {i}", user_id=log_user.id)
        db.session.add(log_entry)
        db.session.commit()

    entries_page = paginate(LogEntry.query_for(log_user), 3, 10)

    assert entries_page
    assert entries_page.items
    assert entries_page.total == 40
    assert entries_page.has_next
    assert entries_page.has_prev
    assert entries_page.pages == 4
    assert entries_page.prev_page == 2
    assert entries_page.next_page == 4

    entries_page = paginate(LogEntry.query_for(log_user), 1, 10)

    assert entries_page
    assert entries_page.items
    assert entries_page.total == 40
    assert entries_page.has_next
    assert not entries_page.has_prev
    assert entries_page.pages == 4
    assert entries_page.next_page == 2

    entries_page = paginate(LogEntry.query_for(log_user), 4, 10)

    assert entries_page
    assert entries_page.items
    assert entries_page.total == 40
    assert not entries_page.has_next
    assert entries_page.has_prev
    assert entries_page.pages == 4
    assert entries_page.prev_page == 3

    with pytest.raises(AttributeError):
        entries_page = paginate(LogEntry.query_for(log_user), 4, -1)

    with pytest.raises(AttributeError):
        entries_page = paginate(LogEntry.query_for(log_user), 0, 10)
