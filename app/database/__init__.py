import math
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

Session = sessionmaker(autocommit=False, autoflush=True)
session = scoped_session(Session)

convention = {
    "ix": 'ix_%(column_0_label)s',
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(column_0_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

sql_alchemy_metadata = MetaData(naming_convention=convention)

Base = declarative_base(metadata=sql_alchemy_metadata)
Base.query = session.query_property()


def init_db(db_uri):
    engine = create_engine(db_uri, pool_recycle=3600)
    Session.configure(bind=engine)
    Base.metadata.bind = engine
    Base.metadata.create_all(bind=engine)


class db():
    @staticmethod
    def drop_all():
        Base.metadata.drop_all(Base.metadata.bind)

    @staticmethod
    def create_all():
        Base.metadata.create_all(Base.metadata.bind)

    session = session


class Page():
    def __init__(self, items, page: int, page_size: int, total: int):
        self.items = items
        self.prev_page = None
        self.next_page = None
        self.has_prev = page > 1
        if self.has_prev:
            self.prev_page = page - 1
        prev_items = (page - 1) * page_size
        self.has_next = prev_items + len(items) < total
        if self.has_next:
            self.next_page = page + 1
        self.total = total
        self.pages = int(math.ceil(total / float(page_size)))


def paginate(query, page: int, page_size: int = 25):
    if page <= 0:
        raise AttributeError('page must be >= 1')
    if page_size <= 0:
        raise AttributeError('page_size must be >= 1')

    items = query.limit(page_size).offset((page - 1) * page_size).all()
    total = query.order_by(None).count()

    return Page(items, page, page_size, total)
