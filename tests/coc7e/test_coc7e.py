"""Test functions specific to Call of Cthulhu."""
import os
import json
import jsonschema
import pytest


from whathappened.auth.models import User  # noqa
from whathappened.campaign.models import Campaign  # noqa

from whathappened.character.coc7e import CoCMechanics
from whathappened.character.coc7e import new_character
from whathappened.character.coc7e import CHARACTER_SCHEMA
from whathappened.character.schema import validate
from whathappened.character.models import Character
from whathappened.character.coc7e.convert import fifth, half, convert_from_dholes
from whathappened.utils.schema import migrate
from whathappened.character.schema.coc7e import migrations, latest

BASEDIR = os.path.abspath(os.path.dirname(__file__))


def test_fifth():
    assert fifth("50") == 10
    assert fifth(50) == 10


def test_half():
    assert half("20") == 10
    assert half(20) == 10


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
                  body=nc,
                  mechanics=CoCMechanics)

    return c


def test_validate_schema():
    schema = load_schema(CHARACTER_SCHEMA)
    jsonschema.Draft7Validator.check_schema(schema)


def test_validate(test_sheet: dict):
    nc = new_character("Test Character", "Classic (1920's)")
    assert nc is not None, nc
    errors = validate(nc, CHARACTER_SCHEMA)
    assert len(errors) == 0, errors


def test_convert_from_dholes(dholes_sheet: dict):
    """Test conversion from a character sheet generated at dholes house."""
    assert dholes_sheet is not None
    converted = convert_from_dholes(dholes_sheet)
    errors = validate(converted, CHARACTER_SCHEMA)
    error_messages = errors
    assert len(errors) == 0, error_messages


def test_personalia_and_attributes(newly_created_character: Character):
    assert newly_created_character.name == "Unknown"
    assert newly_created_character.age == "18"
    assert newly_created_character.description == "Unknown"
    assert newly_created_character.system == 'coc7e'
    assert newly_created_character.game[0] == "Call of Cthulhu TM"
    assert newly_created_character.game[1] == "Classic (1920's)"


def test_skills(newly_created_character: Character):
    skill = newly_created_character.skill('Spot Hidden')
    assert skill is not None
    assert skill['start_value'] == 25


def test_skill(newly_created_character: Character):
    skill_name = "test skill"
    skill = newly_created_character.skill(skill_name)
    assert skill is None

    newly_created_character.add_skill(skillname=skill_name, value=13)
    skill = newly_created_character.skill(skill_name)
    assert skill is not None
    assert skill['value'] == 13

    with pytest.raises(ValueError):
        newly_created_character.add_skill(skillname=skill_name, value=154)

    newly_created_character.set_attribute({'category': 'skill',
                                           'field': skill_name,
                                           'value': 21})

    skill = newly_created_character.skill(skill_name)
    assert skill is not None
    assert skill['value'] == 21


def test_subskill(newly_created_character: Character):
    existing_subskill = newly_created_character.skill('Firearms', 'Handgun')
    assert existing_subskill is not None
    assert existing_subskill['start_value'] == 20, existing_subskill['start_value']

    skill_name = "Science"
    subskill_name = "Biology"

    skill = newly_created_character.skill(skill_name)
    newly_created_character.add_subskill(subskill_name, skill_name)
    subskill = newly_created_character.skill(skill_name, subskill_name)

    assert subskill is not None
    assert subskill['value'] == skill['value']

    with pytest.raises(ValueError):
        newly_created_character.add_subskill(subskill_name, skill_name)

    newly_created_character.set_attribute({'category': 'skill',
                                           'field': skill_name,
                                           'subfield': subskill_name,
                                           'value': 21})

    subskill = newly_created_character.skill(skill_name, subskill_name)
    assert subskill is not None
    assert subskill['value'] == 21


def test_validate_migration_up(test_sheet: dict):
    migrated = migrate(test_sheet,
                       "0.0.4",
                       migrations=migrations)
    errors = validate(migrated,
                      CHARACTER_SCHEMA)
    assert len(errors) == 0, errors


def test_validate_migration_latest(test_sheet: dict):
    errors = validate(migrate(test_sheet,
                              latest,
                              migrations=migrations),
                      CHARACTER_SCHEMA)

    assert len(errors) == 0, errors


def test_validate_migration_up_and_down(test_sheet: dict):
    migrated = migrate(test_sheet.copy(),
                       "0.0.4",
                       migrations=migrations)

    back_down = migrate(migrated, "0.0.1", migrations=migrations)

    assert test_sheet == back_down
