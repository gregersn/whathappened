from sqlalchemy.sql.schema import Column
from sqlalchemy.sql.sqltypes import Integer, String
from whathappened.database import init_db, db, Base, BaseModel


class DataModel(Base):
    __tablename__ = 'test_table'
    id = Column(Integer, primary_key=True)
    title = Column(String(256))


def test_connect_db():
    db_uri = 'sqlite:///whathappened_test_db.sqlite'
    init_db(db_uri)
    db.drop_all()
    db.create_all()

    tests = DataModel.query.all()
    assert len(tests) == 0

    test = DataModel(title='test object')
    db.session.add(test)
    db.session.commit()

    tests = DataModel.query.all()
    assert len(tests) == 1


class SerializeModel(BaseModel):
    __tablename__ = 'test_table_2'
    id = Column(Integer, primary_key=True)
    title = Column(String(256))
    action = Column(String(256))

    _default_fields = [
        "id",
        "title",
        "action"
    ]


def test_serialize():

    data = {'id': None, 'title': 'test object', 'action': 'do it'}

    test = SerializeModel()

    ser = test.to_dict()
    assert ser != data

    test.from_dict(**data)

    ser = test.to_dict()

    assert ser == data
