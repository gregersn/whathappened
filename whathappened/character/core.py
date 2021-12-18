import os
from pathlib import Path
import logging
from typing import Type
from whathappened.character import schema
from whathappened.character.schema import load_schema, build_from_schema, validate

logger = logging.getLogger(__name__)


CHARACTER_SCHEMA_DIR = Path(__file__).parent / 'schema/'


GAMES = {
}

MECHANICS = {
}

GameSystems = []


class CharacterMechanics():
    def __init__(self, parent):
        self.parent = parent

    def game(self):
        raise NotImplementedError

    def validate(self, *args, **kwargs):
        schema_file = CHARACTER_SCHEMA_DIR / f"{self.parent.system}.yml"

        if not schema_file.is_file():
            logger.error(f"Could not find: {schema_file}")
            return [{"path": "/",
                    "message": "This character sheet has no known schema or validation."}]

        return validate(self.parent.body, schema_file)

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

    def skills(self, *args):
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


def new_character(title: str, system: str = None, **kwargs):
    if system is None:
        raise SyntaxError("new_character: System not specified")
    CHARACTER_SCHEMA = CHARACTER_SCHEMA_DIR / f"{system}.yml"
    schema_data = load_schema(CHARACTER_SCHEMA)

    nc = build_from_schema(schema_data)
    nc['title'] = title

    return nc


register_game('landf', 'Lasers and feelings')
