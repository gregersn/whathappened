import pytest

import whathappened.character.coc7e.character


def test_blank_character():
    char = whathappened.character.coc7e.character.new_character("Test Character")

    assert False
