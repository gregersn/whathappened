"""Test functions specific to Call of Cthulhu."""
import os
import json
import pytest

from jsonschema import validate

from app.auth.models import User  # noqa
from app.campaign.models import Campaign  # noqa

from app.character.coc import convert_from_dholes
from app.character.coc import new_character
from app.character.coc import schema_file, load_schema
from app.character.models import Character
from app.character.coc import fifth, half
from app.character.coc import schema_file, load_schema, new_character


BASEDIR = os.path.abspath(os.path.dirname(__file__))


def test_fifth():
    assert fifth("50") == "10"
    assert fifth(50) == "10"


def test_half():
    assert half("20") == "10"
    assert half(20) == "10"


@pytest.fixture(name='dholes_sheet')
def fixture_dholes_sheet() -> dict:
    """Load character sheet from JSON and convert to dict."""
    sheet = None
    filename = os.path.join(BASEDIR, 'testchar_dholes.json')
    with open(filename, 'r') as input_file:
        sheet = json.load(input_file)

    return sheet


@pytest.fixture(name='test_sheet')
def fixture_test_sheet() -> dict:
    """Load character sheet from JSON and convert to dict."""
    sheet = None
    with open(os.path.join(BASEDIR, 'testchar.json'), 'r') as input_file:
        sheet = json.load(input_file)

    return sheet


@pytest.fixture(name="newly_created_character")
def fixture_test_character() -> Character:
    nc = new_character("Test Character", "Classic (1920's)")
    c = Character(title="Test Character",
                  body=json.dumps(nc))

    return c


def test_validate(test_sheet: dict):
    nc = new_character("Test Character", "Classic (1920's)")
    schema = load_schema(schema_file)
    validate(nc, schema=schema)
    validate(test_sheet, schema=schema)


def test_convert_from_dholes(dholes_sheet: dict):
    """Test conversion from a character sheet generated at dholes house."""
    assert dholes_sheet is not None
    schema = load_schema(schema_file)
    converted = convert_from_dholes(dholes_sheet)
    validate(converted, schema=schema)


def test_personalia_and_attributes(newly_created_character: Character):
    assert newly_created_character.name == "Unknown"
    assert newly_created_character.age == "18"
    assert newly_created_character.description == "Unknown"
    assert newly_created_character.gametype == "Classic (1920's)"


def test_skills(newly_created_character: Character):
    skill = newly_created_character.skill('Spot Hidden')
    assert skill is not None
    assert skill['value'] == "25"


def test_skill(newly_created_character: Character):
    skill_name = "test skill"
    skill = newly_created_character.skill(skill_name)
    assert skill is None

    newly_created_character.add_skill(skillname=skill_name, value="13")
    skill = newly_created_character.skill(skill_name)
    assert skill is not None
    assert skill['value'] == "13"

    with pytest.raises(ValueError):
        newly_created_character.add_skill(skillname=skill_name, value="154")

    newly_created_character.set_attribute({'type': 'skill',
                                           'field': skill_name,
                                           'value': '21'})

    skill = newly_created_character.skill(skill_name)
    assert skill is not None
    assert skill['value'] == "21"


def test_subskill(newly_created_character: Character):
    skill_name = "Science"
    subskill_name = "Biology"

    skill = newly_created_character.skill(skill_name)
    newly_created_character.add_subskill(subskill_name, skill_name)
    subskill = newly_created_character.skill(skill_name, subskill_name)

    assert subskill is not None
    assert subskill['value'] == skill['value']

    with pytest.raises(ValueError):
        newly_created_character.add_subskill(subskill_name, skill_name)

    newly_created_character.set_attribute({'type': 'skill',
                                           'field': skill_name,
                                           'subfield': subskill_name,
                                           'value': '21'})

    subskill = newly_created_character.skill(skill_name, subskill_name)
    assert subskill is not None
    assert subskill['value'] == '21'
