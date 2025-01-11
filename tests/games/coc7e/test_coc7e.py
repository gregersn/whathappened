"""Test functions specific to Call of Cthulhu."""

from pathlib import Path
import json
import pytest

from whathappened.auth.models import User  # noqa
from whathappened.campaign.models import Campaign  # noqa

from whathappened.core.sheets.mechanics.coc7e import new_character
from whathappened.core.sheets.mechanics.coc7e.mechanics import CoCMechanics
from whathappened.core.sheets.schema.base import CURRENT_SCHEMA_VERSION
from whathappened.core.sheets.schema.build import validate
from whathappened.character.models import Character
from whathappened.core.sheets.mechanics.coc7e.convert import (
    fifth,
    half,
    convert_from_dholes,
)
from whathappened.core.sheets.schema.utils import migrate

BASEDIR = Path(__file__).parent.absolute()


def test_fifth():
    assert fifth("50") == 10
    assert fifth(50) == 10


def test_half():
    assert half("20") == 10
    assert half(20) == 10


@pytest.fixture(name="dholes_sheet")
def fixture_dholes_sheet() -> dict:
    """Load character sheet from JSON and convert to dict."""
    sheet = None
    filename = BASEDIR / "testchar_dholes.json"
    with open(filename, "r") as input_file:
        sheet = json.load(input_file)

    return sheet


@pytest.fixture(name="test_sheet")
def fixture_test_sheet() -> dict:
    """Load character sheet from JSON and convert to dict."""
    sheet = None
    with open(BASEDIR / "testchar.json", "r") as input_file:
        sheet = json.load(input_file)

    return sheet


@pytest.fixture(name="newly_created_character")
def fixture_test_character() -> Character:
    nc = new_character("Test Character", "Classic (1920's)")
    c = Character(title="Test Character", body=nc, mechanics=CoCMechanics)

    return c


def test_validate(test_sheet: dict, app):
    nc = new_character("Test Character", "Classic (1920's)")
    errors = validate(nc, "coc7e")
    assert len(errors) == 0


def test_convert_from_dholes(dholes_sheet: dict):
    """Test conversion from a character sheet generated at dholes house."""
    assert dholes_sheet is not None
    converted = convert_from_dholes(dholes_sheet)
    errors = validate(converted, "coc7e")
    error_messages = errors
    assert len(errors) == 0, error_messages


def test_personalia_and_attributes(newly_created_character: Character, app):
    assert newly_created_character.name == "Unknown"
    assert newly_created_character.age == "18"
    assert newly_created_character.description == "Unknown"
    assert newly_created_character.system == "coc7e"
    assert newly_created_character.game[0] == "Call of Cthulhu TM"
    assert newly_created_character.game[1] == "Classic (1920's)"


def test_skills(newly_created_character: Character, app):
    skill = newly_created_character.skill("Spot Hidden")
    assert skill is not None
    assert skill["value"] == 25


def test_skill(newly_created_character: Character, app):
    skill_name = "test skill"
    skill = newly_created_character.skill(skill_name)
    assert skill is None

    newly_created_character.mechanics.add_skill(skillname=skill_name, value=13)
    skill = newly_created_character.skill(skill_name)
    assert skill is not None
    assert skill["value"] == 13

    with pytest.raises(ValueError):
        newly_created_character.mechanics.add_skill(skillname=skill_name, value=154)

    newly_created_character.set_attribute(
        {"category": "skill", "field": skill_name, "value": 21}
    )

    skill = newly_created_character.skill(skill_name)
    assert skill is not None
    assert skill["value"] == 21


def test_subskill(newly_created_character: Character, app):
    skill_name = "Science"
    subskill_name = "Biology"

    skill = newly_created_character.skill(skill_name)
    newly_created_character.mechanics.add_subskill(subskill_name, skill_name)
    subskill = newly_created_character.skill(skill_name, subskill_name)

    assert subskill is not None
    assert subskill["value"] == skill["value"]

    with pytest.raises(ValueError):
        newly_created_character.mechanics.add_subskill(subskill_name, skill_name)

    newly_created_character.set_attribute(
        {
            "category": "skill",
            "field": skill_name,
            "subfield": subskill_name,
            "value": 21,
        }
    )

    subskill = newly_created_character.skill(skill_name, subskill_name)
    assert subskill is not None
    assert subskill["value"] == 21


def test_validate_migration_up(test_sheet: dict, app):
    errors = validate(migrate(test_sheet, "0.0.8"), "coc7e")
    assert len(errors) == 0, errors


def test_validate_migration_latest(test_sheet: dict, app):
    errors = validate(migrate(test_sheet, CURRENT_SCHEMA_VERSION), "coc7e")

    assert len(errors) == 0, errors


def test_validate_migration_up_and_down(test_sheet: dict, app):
    migrated = migrate(test_sheet.copy(), "0.0.4")

    back_down = migrate(migrated, "0.0.1")

    assert test_sheet == back_down
