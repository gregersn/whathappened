"""Test functions related to Tales from the Loop."""
from pathlib import Path
import pytest

from jsonschema import validate

from whathappened.character.schema import load_schema
from whathappened.character.tftl import CHARACTER_SCHEMA
from whathappened.character.tftl import new_character
from whathappened.character.models import Character

BASEDIR = BASEDIR = Path(__file__).parent.absolute()


@pytest.fixture(name="newly_created_character")
def fixture_test_character() -> Character:
    nc = new_character("Test Character")
    c = Character(title="Test Character",
                  body=nc)

    return c


def test_validate():
    nc = new_character("Test Character")
    schema = load_schema(CHARACTER_SCHEMA)
    validate(nc, schema=schema)
