from pathlib import Path
import uuid
import logging

from flask import url_for, current_app
from sqlalchemy import event
from sqlalchemy.orm import backref, relationship
from sqlalchemy.sql.schema import Column, ForeignKey
from sqlalchemy.sql.sqltypes import Integer, String
from whathappened.database import Base
from whathappened.models import GUID
from werkzeug.utils import secure_filename

logger = logging.getLogger(__name__)


class Asset(Base):
    ASSET_ORDER = "[Asset.folder_id, Asset.filename]"
    __tablename__ = "asset"
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    filename = Column(String(128))
    owner_id = Column(Integer, ForeignKey("user_profile.id"))
    owner = relationship(
        "UserProfile",
        backref=backref(
            "assets", lazy="dynamic", order_by=ASSET_ORDER, cascade_backrefs=False
        ),
    )
    folder_id = Column(GUID(), ForeignKey("asset_folder.id"))
    folder = relationship("AssetFolder", back_populates="files")

    def __init__(self, *args, **kwargs):
        super(Asset, self).__init__(*args, **kwargs)
        self.loaded = False
        self.data = None

    @property
    def path(self):
        return self.folder.get_path() / self.filename

    @property
    def url(self):
        return url_for("userassets.view", fileid=self.id, filename=self.filename)

    @property
    def system_path(self):
        return self.folder.system_path / secure_filename(str(self.filename))


@event.listens_for(Asset, "before_delete")
def before_asset_delete(mapper, connection, target):
    logger.debug("Asset is being deleted")
    logger.debug(target.filename)
    system_folder = Path(current_app.config["UPLOAD_FOLDER"])
    filepath: Path = target.folder.get_path()
    assetname = secure_filename(target.filename)
    logger.debug(f"Deleting file from {filepath}, {assetname}")
    full_dir = system_folder / filepath
    full_file_path = full_dir / assetname
    if full_file_path.is_file():
        logger.debug("Delete the actual file")
        full_file_path.unlink()


class AssetFolder(Base):
    __tablename__ = "asset_folder"
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    owner_id = Column(Integer, ForeignKey("user_profile.id"))
    owner = relationship(
        "UserProfile",
        backref=backref("assetfolders", lazy="dynamic", cascade_backrefs=False),
    )
    parent_id = Column(GUID(), ForeignKey("asset_folder.id"), default=None)
    subfolders = relationship(
        "AssetFolder", backref=backref("parent", remote_side=[id])
    )
    title = Column(String(128))
    files = relationship("Asset", back_populates="folder")

    def get_path(self) -> Path:
        if self.parent:
            parent = self.parent.get_path()
            return parent / secure_filename(str(self.title))
        else:
            return Path(str(self.id)) / secure_filename(str(self.title))

    @property
    def path(self) -> Path:
        if self.parent:
            parent = self.parent.path
            return parent / self.title
        else:
            return Path(str(self.title))

    @property
    def system_path(self) -> Path:
        return Path(current_app.config["UPLOAD_FOLDER"]) / self.get_path()
