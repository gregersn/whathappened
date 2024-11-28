import json
import logging
from typing import Any, Dict, Type
from datetime import datetime

from sqlalchemy.orm.attributes import flag_modified
from sqlalchemy.orm import reconstructor, relationship, backref
from sqlalchemy.sql.schema import Column, ForeignKey
from sqlalchemy.sql.sqltypes import DateTime, Integer, JSON, String

from whathappened.database.base import BaseModel
from whathappened.sheets.mechanics.core import CharacterMechanics, MECHANICS
from whathappened.content.mixins import BaseContent

logger = logging.getLogger(__name__)


class Character(BaseContent, BaseModel):
    __tablename__ = "charactersheet"
    id = Column(Integer, primary_key=True)
    title = Column(String(256))
    body = Column(JSON)
    timestamp = Column(
        DateTime, index=True, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    user_id = Column(Integer, ForeignKey("user_profile.id"))
    player = relationship("UserProfile", backref=backref("characters", lazy="dynamic"))

    folder = relationship("Folder", backref="characters")

    _default_fields = ["id", "title", "body", "timestamp", "user_id"]

    def __repr__(self):
        return "<Character {}>".format(self.title)

    def __init__(
        self, mechanics: Type[CharacterMechanics] = CharacterMechanics, *args, **kwargs
    ):
        super(Character, self).__init__(*args, **kwargs)
        self._data = None
        # Add a subclass or something that
        # has the mechanics of the character.
        self.mechanics = mechanics(self)

    @reconstructor
    def init_on_load(self):
        system = self.data.get("system", "")
        logger.debug(f"Loading character of type {system}")
        system = self.system
        self.mechanics = MECHANICS.get(system, CharacterMechanics)(self)

    @property
    def data(self) -> Dict[str, Any]:
        if isinstance(self.body, dict):
            logger.debug("%s: Character data is dict", self.id)
            return self.body
        if isinstance(self.body, str):
            logger.warning(f"Character, id {self.id} body is string, not dictionary")
            return json.loads(self.body)
        logger.error("Body is not a dictionary")
        return {}

    @property
    def system(self) -> str:
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
    def version(self):
        v = self.data.get("version", None)
        return v

    @property
    def game(self):
        return self.mechanics.game()

    def validate(self):
        return self.mechanics.validate()

    def get_sheet(self):
        return self.data

    @property
    def name(self):
        return self.mechanics.name

    @property
    def age(self):
        return self.mechanics.age

    @property
    def portrait(self):
        return self.mechanics.portrait

    @property
    def description(self):
        return self.mechanics.description

    def set_attribute(self, attribute: Dict):
        """Set a specific attribute."""
        return self.mechanics.set_attribute(attribute)

    def store_data(self):
        """Mark data as modified."""
        flag_modified(self, "body")

    def skill(self, *args, **kwargs):
        return self.mechanics.skill(*args, **kwargs)

    def skills(self, *args):
        """Return a list of skills."""
        return self.data["skills"]

    @property
    def schema_version(self):
        return self.data["meta"]["Version"]
