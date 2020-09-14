import os
import json
import pytest

from app.charactersheet.coc import convert_from_dholes, convert_to_dholes

basedir = os.path.abspath(os.path.dirname(__file__))


@pytest.fixture
def dholes_sheet():
    sheet = None
    with open(os.path.join(basedir, 'testchar.json'), 'r') as f:
        sheet = json.load(f)

    return sheet


def test_convert_from_dholes(dholes_sheet):
    assert dholes_sheet is not None
    converted = convert_from_dholes(dholes_sheet)

    sheet_sections = ['meta', 'personalia', 'characteristics',
                      'skills', 'weapons', 'combat', 'backstory',
                      'possessions', 'cash', 'assets']

    for section in sheet_sections:
        assert section in converted

    skills = converted['skills']
    assert type(skills) == list

    skill_names = ['Accounting', 'Appraise', 'Cthulhu Mythos']
    for skill in skills:
        if skill['name'] in skill_names:
            skill_names.remove(skill['name'])

    assert len(skill_names) == 0

    weapons = converted['weapons']
    assert type(weapons) == list

    possessions = converted['possessions']
    assert type(possessions) == list


def test_convert_from_dholes_and_back(dholes_sheet):
    converted = convert_to_dholes(convert_from_dholes(dholes_sheet))

    assert dholes_sheet == converted

