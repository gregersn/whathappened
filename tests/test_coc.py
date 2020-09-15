"""Test functions specific to Call of Cthulhu."""
import os
import json
import pytest

from app.charactersheet.coc import convert_from_dholes, convert_to_dholes

BASEDIR = os.path.abspath(os.path.dirname(__file__))


@pytest.fixture(name='dholes_sheet')
def fixture_dholes_sheet() -> dict:
    """Load character sheet from JSON and convert to dict."""
    sheet = None
    with open(os.path.join(BASEDIR, 'testchar_dholes.json'), 'r') as input_file:
        sheet = json.load(input_file)

    return sheet


@pytest.fixture(name='test_sheet')
def fixture_test_sheet() -> dict:
    """Load character sheet from JSON and convert to dict."""
    sheet = None
    with open(os.path.join(BASEDIR, 'testchar.json'), 'r') as input_file:
        sheet = json.load(input_file)

    return sheet


def test_convert_from_dholes(dholes_sheet: dict, test_sheet: dict):
    """Test conversion from a character sheet generated at dholes house."""
    assert dholes_sheet is not None
    converted = convert_from_dholes(dholes_sheet)

    sheet_sections = ['meta', 'personalia', 'characteristics',
                      'skills', 'weapons', 'combat', 'backstory',
                      'possessions', 'cash', 'assets']

    for section in sheet_sections:
        assert section in converted

    skills = converted['skills']
    assert isinstance(skills, list)

    skill_names = ['Accounting', 'Appraise', 'Cthulhu Mythos']
    for skill in skills:
        if skill['name'] in skill_names:
            skill_names.remove(skill['name'])

    assert not skill_names

    weapons = converted['weapons']
    assert isinstance(weapons, list)

    possessions = converted['possessions']
    assert isinstance(possessions, list)

    assert converted == test_sheet


def test_convert_from_to_dholes(dholes_sheet: dict):
    """Test conversion from dholes and back to dholes."""
    converted = convert_to_dholes(convert_from_dholes(dholes_sheet))

    assert dholes_sheet == converted
