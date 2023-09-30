from whathappened.sheets.schema.build import build_from_schema, get_schema, validate
from whathappened.sheets.schema import dod


def test_new_character():
    data = dod.CharacterSheet().model_dump()
    assert data
    assert data["system"] == "dod"
    assert data["meta"]
    assert data["meta"]["title"] == "Unknown"
    assert data["meta"]["gamename"] == "Drakar och Demoner"
    assert data["character_sheet"]


def test_new_character_from_schema():
    data = get_schema("dod")
    nc = build_from_schema(data)

    assert nc["character_sheet"]["slakte"] == "Människa"
    assert not isinstance(nc["character_sheet"]["fardigheter"], str)

    assert not validate(nc, "dod")
