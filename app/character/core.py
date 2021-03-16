import logging
from typing import Type, Dict, List, Tuple

logger = logging.getLogger(__name__)

GAMES: Dict[str, str] = {
}

MECHANICS: Dict[str, Type['CharacterMechanics']] = {
}

GameSystems: List[Tuple[str, str]] = []


class CharacterMechanics():
    def __init__(self, parent):
        self.parent = parent

    def game(self) -> None:
        raise NotImplementedError

    def validate(self, *args, **kwargs):
        logger.error("validate: Not implemented")
        return [{"path": "/", "message": "This character sheet has no known schema or validation."}]

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
