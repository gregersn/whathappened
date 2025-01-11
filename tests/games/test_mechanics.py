import pytest
from whathappened.core.sheets.mechanics.core import CharacterMechanics
from whathappened.core.sheets.utils import create_sheet


@pytest.fixture
def sheet():
    return create_sheet("landf")


class Character:
    def __init__(self, data):
        self.body = data

    @property
    def system(self):
        return self.body["system"]


@pytest.fixture
def character():
    return Character(create_sheet("landf"))


def test_validate(sheet):
    character = Character(sheet)
    assert character.system == "landf"
    mechanics = CharacterMechanics(character)
    assert not mechanics.validate()


def test_attributes(character):
    mechanics = CharacterMechanics(character)
    assert mechanics.attribute("character_sheet.name") == "Ace"

    assert mechanics.attribute("character_sheet.stat") == 4

    mechanics.set_attribute({"field": "character_sheet.stat", "value": 5})

    assert mechanics.attribute("character_sheet.stat") == 5
