from whathappened.character.models import Character
from whathappened.character.forms import ImportForm
from typing import ChainMap


def test_create_character(db):
    character = Character(title='test_character')
    db.session.add(character)
    db.session.commit()

    characters = Character.query.all()
    assert character in characters
    assert str(character) == '<Character test_character>'


def test_edit_json(app):
    form = ImportForm()
    assert not form.validate()


def test_character_diff():
    blank_character = {
        'strength': 1,
        'dexterity': 1
    }

    created_character = {
    }

    character = ChainMap(created_character, blank_character)

    assert character['strength'] == 1
    assert character['dexterity'] == 1

    character['strength'] = 2

    assert character['strength'] == 2
    assert character['dexterity'] == 1

    assert blank_character['strength'] == 1
    assert blank_character['dexterity'] == 1

    assert created_character['strength'] == 2
