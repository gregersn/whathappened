from pathlib import Path
import uuid
import logging

from sqlalchemy import event
from sqlalchemy.orm import backref, relationship, Mapped, mapped_column
from sqlalchemy.sql.schema import ForeignKey
from sqlalchemy.sql.sqltypes import String
from werkzeug.utils import secure_filename

from whathappened.core.database import Base
from whathappened.core.database.models import GUID, UserProfile

logger = logging.getLogger(__name__)


class Asset(Base):
    ASSET_ORDER = "[Asset.folder_id, Asset.filename]"
    __tablename__ = "asset"
    id: Mapped[str] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    filename: Mapped[str] = mapped_column(String(128), nullable=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("user_profile.id"), nullable=True)
    owner: Mapped[UserProfile] = relationship(
        backref=backref(
            "assets", lazy="dynamic", order_by=ASSET_ORDER, cascade_backrefs=False
        ),
    )
    folder_id: Mapped[str] = mapped_column(
        GUID(), ForeignKey("asset_folder.id"), nullable=True
    )
    folder: Mapped["AssetFolder"] = relationship(back_populates="files")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.loaded = False
        self.data = None

    @property
    def path(self):
        return self.folder.get_path() / self.filename

    def get_path(self):
        return self.folder.get_path() / secure_filename(str(self.filename))


@event.listens_for(Asset, "before_delete")
def before_asset_delete(mapper, connection, target):
    logger.debug("Asset is being deleted")
    logger.debug(target.filename)
    filepath: Path = target.folder.get_path()
    assetname = secure_filename(target.filename)
    logger.debug(f"Deleting file from {filepath}, {assetname}")
    full_dir = filepath
    full_file_path = full_dir / assetname
    if full_file_path.is_file():
        logger.debug("Delete the actual file")
        full_file_path.unlink()


class AssetFolder(Base):
    __tablename__ = "asset_folder"
    id: Mapped[str] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    owner_id: Mapped[int] = mapped_column(ForeignKey("user_profile.id"), nullable=True)
    owner: Mapped[UserProfile] = relationship(
        backref=backref("assetfolders", lazy="dynamic", cascade_backrefs=False),
    )
    parent_id: Mapped[str] = mapped_column(
        GUID(), ForeignKey("asset_folder.id"), default=None, nullable=True
    )
    subfolders: Mapped[list["AssetFolder"]] = relationship(back_populates="parent")
    parent: Mapped["AssetFolder"] = relationship(
        back_populates="subfolders", remote_side=[id]
    )
    title: Mapped[str] = mapped_column(String(128), nullable=True)
    files: Mapped[list[Asset]] = relationship(back_populates="folder")

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
