from sqlalchemy import Column, ForeignKey
from sqlalchemy.ext.declarative import declared_attr

from app.database.fields import GUID


class BaseContent():
    @declared_attr
    def folder_id(cls):
        return Column(GUID(), ForeignKey('folder.id'),
                      nullable=True, default=None)
