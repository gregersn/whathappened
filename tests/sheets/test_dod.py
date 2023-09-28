from whathappened.sheets.schema.build import build_from_schema
from whathappened.sheets.schema import dod


def test_new_character():
    data = dod.CharacterSheet().model_dump()
    assert data
    assert data["system"] == "dod"
    assert data["meta"]
    assert data["meta"]["title"] == "Unknown"
    assert data["meta"]["gamename"] == "Drakar och Demoner"
    assert data["character_sheet"]
