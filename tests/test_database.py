import os
from sqlalchemy.sql.schema import Column
from sqlalchemy.sql.sqltypes import Integer, String
from app.database import init_db, db, Base


class TestModel(Base):
    __tablename__ = 'test_table'
    id = Column(Integer, primary_key=True)
    title = Column(String(256))


def test_connect_db():
    db_uri = 'sqlite:///whathappened_test_db.sqlite'
    init_db(db_uri)
    db.drop_all()
    db.create_all()

    tests = TestModel.query.all()
    assert len(tests) == 0

    test = TestModel(title='test object')
    db.session.add(test)
    db.session.commit()

    tests = TestModel.query.all()
    assert len(tests) == 1
