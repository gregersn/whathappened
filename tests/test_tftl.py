"""Test functions related to Tales from the Loop."""
import os
import json
import pytest

from jsonschema import validate

from app.character.schema import load_schema
from app.character.tftl import schema_file
from app.character.tftl import new_character
from app.character.models import Character

BASEDIR = os.path.abspath(os.path.dirname(__file__))


@pytest.fixture(name='test_sheet')
def fixture_test_sheet() -> dict:
    """Load character sheet from JSON and convert to dict."""
    sheet = None
    with open(os.path.join(BASEDIR, 'testchar.json'), 'r') as input_file:
        sheet = json.load(input_file)

    return sheet


@pytest.fixture(name="newly_created_character")
def fixture_test_character() -> Character:
    nc = new_character("Test Character")
    c = Character(title="Test Character",
                  body=nc)

    return c


def test_validate(test_sheet: dict):
    nc = new_character("Test Character")
    schema = load_schema(schema_file)
    validate(nc, schema=schema)
