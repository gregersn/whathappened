from whathappened.sheets.schema import landf


def test_new_character():
    data = landf.CharacterSheet().model_dump()
    assert data
    assert data["system"] == "landf"
    assert data["meta"]
    assert data["meta"]["title"] == "Unknown"
    assert data["meta"]["gamename"] == "Lasers and feelings"
    assert data["character_sheet"]

    assert landf.CharacterSheet.model_validate(data)