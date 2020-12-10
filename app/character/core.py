from typing import Type

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
        raise NotImplementedError

    def name(self):
        raise NotImplementedError

    def age(self):
        raise NotImplementedError

    def portrait(self):
        raise NotImplementedError

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


def register_game(tag: str,
                  name: str,
                  mechanics: Type[CharacterMechanics] = CharacterMechanics):
    global GameSystems
    GAMES[tag] = name
    MECHANICS[tag] = mechanics

    GameSystems.clear()
    GameSystems += [(k, v) for k, v in GAMES.items()]
