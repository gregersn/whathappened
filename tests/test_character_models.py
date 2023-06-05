from whathappened.character.models import Character


def test_create_character(db):
    character = Character(title='test_character')
    db.session.add(character)
    db.session.commit()

    characters = Character.query.all()
    assert character in characters
    assert str(character) == '<Character test_character>'
