from sqlalchemy import create_engine
from sqlalchemy.pool import NullPool
from .base import Base, Session, session


def init_db(db_uri, nullpool: bool = False):
    if nullpool:
        engine = create_engine(db_uri, poolclass=NullPool, future=True)
    else:
        engine = create_engine(db_uri, pool_recycle=3600, future=True)
    Session.configure(bind=engine)
    Base.metadata.bind = engine
    Base.metadata.create_all(bind=engine)


class db:
    @staticmethod
    def drop_all():
        Base.metadata.drop_all(Base.metadata.bind)

    @staticmethod
    def create_all():
        breakpoint()
        Base.metadata.create_all(Base.metadata.bind)

    session = session
