import json
from typing import KeysView, List, Dict, Any, Optional

from sqlalchemy import MetaData, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm.attributes import QueryableAttribute
from sqlalchemy.sql.elements import not_
from sqlalchemy.orm import sessionmaker

from whathappened.config import Config

SQL_ALCHEMY_DATABASE_URL = Config.SQLALCHEMY_DATABASE_URI

assert isinstance(SQL_ALCHEMY_DATABASE_URL, str)

engine = create_engine(SQL_ALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=True, bind=engine)

convention = {
    "ix": 'ix_%(column_0_label)s',
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(column_0_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

sql_alchemy_metadata = MetaData(naming_convention=convention)

Base = declarative_base(metadata=sql_alchemy_metadata)
# Base.query = session.query_property()


class BaseModel(Base):
    """Base database model for WhatHappened.

    Adds dictionary serialization.

    Serialization code from
    https://medium.com/@alanhamlett/part-1-sqlalchemy-models-to-json-de398bc2ef47
    """
    __abstract__ = True

    def to_dict(self, show: Optional[List[str]] = None, _hide: List[str] = [], _path: Optional[str] = None) -> Dict[str, Any]:
        """Return a dictionary representation of model."""

        show = show or []

        hidden: List[str] = self._hidden_fields if hasattr(self, "_hidden_fields") else []
        default: List[str] = self._default_fields if hasattr(self, "_default_fields") else []

        default.extend(['id', 'modified_at', 'created_at'])

        if not _path:
            _path = self.__tablename__.lower()

            def prepend_path(item: str) -> str:
                item = item.lower()
                if item.split(".", 1)[0] == _path:
                    return item
                if len(item) == 0:
                    return item
                if item[0] != ".":
                    item = f".{item}"
                item = f"{_path}{item}"
                return item

            _hide[:] = [prepend_path(x) for x in _hide]
            show[:] = [prepend_path(x) for x in show]

        columns: KeysView[str] = self.__table__.columns.keys()
        relationships: KeysView[str] = self.__mapper__.relationships.keys()
        properties = dir(self)

        ret_data: Dict[str, Any] = {}

        for key in columns:
            if key.startswith("_"):
                continue

            check = f"{_path}.{key}"

            if check in _hide or key in hidden:
                continue

            if check in show or key in default:
                ret_data[key] = getattr(self, key)

        for key in relationships:
            if key.startswith("_"):
                continue

            check = f"{_path}.{key}"

            if check in _hide or key in hidden:
                continue

            if check in show or key in default:
                _hide.append(check)
                is_list = self.__mapper__.relationships[key].uselist
                if is_list:
                    items = getattr(self, key)
                    if self.__mapper__.relationships[key].query_class is not None:
                        if hasattr(items, "all"):
                            items = items.all()
                    ret_data[key] = []
                    for item in items:
                        ret_data[key].append(item.to_dict(show=list(show), _hide=list(_hide), _path=f"{_path}.{key.lower()}"))
                else:
                    if (self.__mapper__.relationships[key].query_class is not None
                            or self.__mapper__.relationships[key].instrument_class is not None):
                        item = getattr(self, key)
                        if item is not None:
                            ret_data[key] = item.to_dict(show=list(show), _hide=list(_hide), _path=f"{_path}.{key.lower()}")
                        else:
                            ret_data[key] = None
                    else:
                        ret_data[key] = getattr(self, key)

        for key in list(set(properties) - set(columns) - set(relationships)):
            if key.startswith("_"):
                continue

            if not hasattr(self.__class__, key):
                continue

            attr = getattr(self.__class__, key)

            if not (isinstance(attr, property) or isinstance(attr, QueryableAttribute)):
                continue

            check = f"{_path}.{key}"
            if check in _hide or key in hidden:
                continue

            if check in show or key in default:
                val = getattr(self, key)
                if hasattr(val, "to_dict"):
                    ret_data[key] = val.to_dict(show=list(show), _hide=list(_hide), _path=f"{_path}.{key.lower()}")
                else:
                    try:
                        ret_data[key] = json.loads(json.dumps(val))
                    except Exception:
                        pass

        return ret_data

    def from_dict(self, **kwargs):
        """Update model with dictionary."""

        _force = kwargs.pop("_force", False)

        readonly = self._readonly_fields if hasattr(self, "_readonly_fields") else []

        if hasattr(self, "_hidden_fields"):
            readonly += self._hidden_fields

        readonly += ["id", "created_at", "modified_at"]

        columns = self.__table__.columns.keys()
        relationships = self.__mapper__.relationships.keys()
        properties = dir(self)

        changes = {}

        for key in columns:
            if key.startswith("_"):
                continue
            allowed = True if _force or key not in readonly else False
            exists = True if key in kwargs else False
            if allowed and exists:
                val = getattr(self, key)
                if val != kwargs[key]:
                    changes[key] = {"old": val, "new": kwargs[key]}
                    setattr(self, key, kwargs[key])

        for rel in relationships:
            if rel.startswith('_'):
                continue
            allowed = True if _force or rel not in readonly else False
            exists = True if rel in kwargs else False

            if allowed and exists:
                is_list = self.__mapper__.relationships[rel].uselist
                if is_list:
                    valid_ids = []
                    query = getattr(self, rel)
                    cls = self.__mapper__.relationships[rel].argument()
                    for item in kwargs[rel]:
                        if ("id" in item and query.filter_by(id=item["id"]).limit(1).count() == 1):
                            obj = cls.query.filter_by(id=item["id"]).first()
                            col_changes = obj.from_dict(**item)
                            if col_changes:
                                col_changes["id"] = str(item["id"])
                                if rel in changes:
                                    changes[rel].append(col_changes)
                                else:
                                    changes.update({rel: [col_changes]})
                                    valid_ids.append(str(item["id"]))
                        else:
                            col = cls()
                            col_changes = col.from_dict(**item)
                            query.append(col)
                            session.flush()
                            if col_changes:
                                col_changes["id"] = str(col.id)
                                if rel in changes:
                                    changes[rel].append(col_changes)
                                else:
                                    changes.update({rel: [col_changes]})
                            valid_ids.append(str(col.id))
                    # delete rows from relationship not in kwargs[rel]
                    for item in query.filter(not_(cls.id.in_(valid_ids))).all():
                        col_changes = {"id": str(item.id), "deleted": True}
                        if rel in changes:
                            changes[rel].append(col_changes)
                        else:
                            changes.update({rel: [col_changes]})
                        session.delete(item)
                else:
                    val = getattr(self, rel)
                    if self.__mapper__.relationships[rel].query_class is not None:
                        if val is not None:
                            col_changes = val.from_dict(**kwargs[rel])

                            if col_changes:
                                changes.update({rel: col_changes})
                    else:
                        if val != kwargs[rel]:
                            setattr(self, rel, kwargs[rel])
                            changes[rel] = {"old": val, "new": kwargs[rel]}
        for key in list(set(properties) - set(columns) - set(relationships)):
            if key.startswith("_"):
                continue
            allowed = True if _force or key not in readonly else False
            exists = True if key in kwargs else False
            if allowed and exists \
                    and getattr(self.__class__, key).fset is not None:
                val = getattr(self, key)
                if hasattr(val, "to_dict"):
                    val = val.to_dict()
                changes[key] = {"old": val, "new": kwargs[key]}
                setattr(self, key, kwargs[key])

        return changes


def init_db(db_uri):
    engine = create_engine(db_uri, pool_recycle=3600)
    SessionLocal.configure(bind=engine)
    Base.metadata.bind = engine
    Base.metadata.create_all(bind=engine)


class db():

    @staticmethod
    def drop_all():
        Base.metadata.drop_all(Base.metadata.bind)

    @staticmethod
    def create_all():
        Base.metadata.create_all(Base.metadata.bind)

    session = SessionLocal
