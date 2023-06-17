from sqlalchemy import Column, ForeignKey
from sqlalchemy.orm import declared_attr

from whathappened.database.fields import GUID


class BaseContent():
    @declared_attr
    def folder_id(cls):
        return Column(GUID(), ForeignKey('folder.id'),
                      nullable=True, default=None)
