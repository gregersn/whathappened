from whathappened.database.models import Character
from whathappened.character.forms import ImportForm


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
