"""Test functions related to Tales from the Loop."""

from pathlib import Path
import pytest


from whathappened.sheets.mechanics.tftl import new_character
from whathappened.character.models import Character

BASEDIR = BASEDIR = Path(__file__).parent.absolute()


@pytest.fixture(name="newly_created_character")
def fixture_test_character() -> Character:
    nc = new_character("Test Character")
    c = Character(title="Test Character", body=nc)

    return c
