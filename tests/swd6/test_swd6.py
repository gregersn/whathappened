"""Test functions related to Star Wars WEG D6."""
import os
import yaml
import pytest

from jsonschema import validate

from app.character.schema import load_schema
from app.character.swd6 import CHARACTER_SCHEMA
from app.character.swd6 import new_character
from app.character.models import Character

BASEDIR = os.path.abspath(os.path.dirname(__file__))


@pytest.fixture(name="newly_created_character")
def fixture_test_character() -> Character:
    nc = new_character("Test Character")
    c = Character(title="Test Character",
                  body=nc)

    return c


def test_validate_schema():
    schema = load_schema(os.path.join(os.path.dirname(__file__),
                                      '../../app/character/character_sheet.yaml'))

    with open(CHARACTER_SCHEMA, 'r') as f:
        data = yaml.safe_load(f)

        validate(data, schema=schema)


def test_validate():
    nc = new_character("Test Character")
    schema = load_schema(CHARACTER_SCHEMA)
    validate(nc, schema=schema)
