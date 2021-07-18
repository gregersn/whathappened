import pytest

import app.character.coc7e.character


def test_blank_character():
    char = app.character.coc7e.character.new_character("Test Character")

    assert False
