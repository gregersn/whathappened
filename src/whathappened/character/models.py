"""Character models."""

import json
import logging
from typing import Any, Dict, Type
from datetime import datetime

from sqlalchemy.orm.attributes import flag_modified
from sqlalchemy.orm import reconstructor, relationship, backref, Mapped, mapped_column
from sqlalchemy.sql.schema import ForeignKey
from sqlalchemy.sql.sqltypes import DateTime, JSON, String

from whathappened.models import UserProfile
from whathappened.database.base import BaseModel
from whathappened.sheets.mechanics.core import CharacterMechanics, MECHANICS
from whathappened.content.mixins import BaseContent
from whathappened.content.models import Folder

logger = logging.getLogger(__name__)


class Character(BaseContent, BaseModel):
    """Character sheet storage."""

    __tablename__ = "charactersheet"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(256), nullable=True)
    body = mapped_column(JSON)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime,
        index=True,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=True,
    )
    user_id: Mapped[int] = mapped_column(ForeignKey("user_profile.id"), nullable=True)
    player: Mapped[UserProfile] = relationship(
        backref=backref("characters", lazy="dynamic")
    )

    folder: Mapped[Folder] = relationship(backref="characters")

    _default_fields = ["id", "title", "body", "timestamp", "user_id"]

    def __repr__(self):
        return f"<Character {self.title}>"

    def __init__(
        self, *args, mechanics: Type[CharacterMechanics] = CharacterMechanics, **kwargs
    ):
        super().__init__(*args, **kwargs)
        self._data = None
        # Add a subclass or something that
        # has the mechanics of the character.
        self.mechanics = mechanics(self)

    @reconstructor
    def init_on_load(self):
        """Initialize object on loading."""
        system = self.data.get("system", "")
        logger.debug("Loading character of type %s", system)
        system = self.system
        self.mechanics = MECHANICS.get(system, CharacterMechanics)(self)

    @property
    def data(self) -> Dict[str, Any]:
        """Character data."""
        if isinstance(self.body, dict):
            return self.body
        if isinstance(self.body, str):
            logger.warning("Character, id %s body is string, not dictionary", self.id)
            return json.loads(self.body)
        logger.error("Body is not a dictionary")
        return {}

    @property
    def system(self) -> str:
        """Character system."""
        s = self.data.get("system", None)
        if s is not None:
            return s

        logger.warning("Deprecation: Outdated character data")
        default = "Call of Cthulhu TM"
        if self.data.get("meta", {}).get("GameName") == default:
            logger.warning("Trying old CoC stuff.")
            return "coc7e"

        return "Unknown"

    @property
    def game(self):
        """Character sheet game."""
        return self.mechanics.game()

    def validate(self):
        """Validate character."""
        return self.mechanics.validate()

    def get_sheet(self):
        """Character sheet."""
        return self.data

    @property
    def name(self):
        """Character name."""
        return self.mechanics.name

    @property
    def age(self):
        """Character age."""
        return self.mechanics.age

    @property
    def portrait(self):
        """Character portrait."""
        return self.mechanics.portrait

    @property
    def description(self):
        """Character description."""
        return self.mechanics.description

    def set_attribute(self, attribute: Dict):
        """Set a specific attribute."""
        return self.mechanics.set_attribute(attribute)

    def store_data(self):
        """Mark data as modified."""
        flag_modified(self, "body")

    def skill(self, *args, **kwargs):
        """Get skill."""
        return self.mechanics.skill(*args, **kwargs)

    def skills(self, *_):
        """Return a list of skills."""
        return self.data["character_sheet"]["skills"]

    @property
    def schema_version(self):
        """Version of schema."""
        return self.data["meta"]["Version"]

    def viewable_by(self, player: UserProfile):
        """Check if character is viewable."""
        if self.player == player:
            return True

        for campaign_association in self.campaign_associations:
            if campaign_association.campaign.user == player:
                return True

            if (
                campaign_association.share_with_players
                or campaign_association.group_sheet
            ) and player in campaign_association.campaign.players:
                return True

        return False

    def editable_by(self, player: UserProfile):
        """Check if character is editable."""
        if self.player == player:
            return True

        for campaign_association in self.campaign_associations:
            if (
                campaign_association.editable_by_gm
                and campaign_association.campaign.user == player
            ):
                return True

            if (
                campaign_association.group_sheet
                and player in campaign_association.campaign.players
            ):
                return True

        return False
