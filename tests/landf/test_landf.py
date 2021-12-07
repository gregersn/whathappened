from whathappened.character.core import CharacterMechanics, new_character


def test_new_character():
    nc = new_character('landf')
    print(nc)
    print(type(nc))
    assert isinstance(nc, CharacterMechanics)
    assert nc.system == 'landf'
    assert nc.schema_file is not None
    assert nc.data['character_sheet']['name'] == 'Ace'

    saved = nc.save()
    assert saved == {'system': 'landf'}, saved

    nc.data['character_sheet']['name'] = 'Base'

    saved = nc.save()

    assert saved == {'character_sheet': {
        'name': 'Base'}, 'system': 'landf'}, saved
