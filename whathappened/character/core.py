from pathlib import Path
import logging
from typing import Any, Dict, Optional, Type
from whathappened.utils.collections import ChainedSheet
from whathappened.character.schema import load_schema, build_from_schema, validate


logger = logging.getLogger(__name__)


CHARACTER_SCHEMA_DIR = Path(__file__).parent / 'schema'


GAMES = {
}

MECHANICS: Dict[str, Type['CharacterMechanics']] = {
}

GameSystems = []


class CharacterMechanics():
    system: Optional[str] = None
    _basedata: Optional[Dict[str, Any]] = None
    _data: Dict[str, Any] = {}
    data: ChainedSheet

    def __init__(self, data, system: Optional[str] = None):
        # self.parent = parent
        self._data = data
        self.system = system
        self.data = ChainedSheet(self._data, self.base_data)

    def game(self):
        raise NotImplementedError

    def validate(self, *args, **kwargs):
        return None
        schema_file = self.schema_file

        if not schema_file or not schema_file.exists():
            logger.error(f"Could not find: {schema_file}")
            return [{"path": "/",
                    "message": "This character sheet has no known schema or validation."}]

        return validate(self.data, schema_file)

    @property
    def schema_file(self) -> Optional[Path]:
        if self.system is not None:
            return CHARACTER_SCHEMA_DIR / (self.system + '.yaml')

    @property
    def base_data(self) -> Dict[str, Any]:
        if self.schema_file and not self._basedata:
            self._basedata = build_from_schema(load_schema(self.schema_file))
        return self._basedata or {}

    def save(self) -> Dict[str, Any]:
        return self.data.changes() or {}

    @property
    def name(self):
        logger.error("name: Not implemented")
        return "Unknown property, name"

    @property
    def age(self):
        logger.error("age: Not implemented")
        return "Unknown property, age"

    @property
    def description(self):
        logger.error("description: Not implemented")
        return "Unknown property, description"

    def portrait(self):
        logger.error("portrait: Not implemented")
        return "Unknown property, portrait"

    def attribute(self, *args):
        raise NotImplementedError

    def set_attribute(self, attribute):
        raise NotImplementedError

    def store_data(self):
        return

    def skill(self, skill, subskill=None):
        raise NotImplementedError

    def add_skill(self, *args, **kwargs):
        raise NotImplementedError

    def add_subskill(self, *args, **kwargs):
        raise NotImplementedError

    def set_portrait(self, data: str):
        raise NotImplementedError


def register_game(tag: str,
                  name: str,
                  mechanics: Type[CharacterMechanics] = CharacterMechanics):
    global GameSystems
    GAMES[tag] = name
    MECHANICS[tag] = mechanics

    GameSystems.clear()
    GameSystems += [(k, v) for k, v in GAMES.items()]


def new_character(system: str, **kwargs) -> CharacterMechanics:
    mechanics = MECHANICS.get(system, None)
    if mechanics is None:
        raise Exception(f"Unknown game system: {system}")
    return mechanics({'system': system}, system=system)


register_game('landf', 'Lasers and feelings')
