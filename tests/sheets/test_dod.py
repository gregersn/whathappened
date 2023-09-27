from whathappened.sheets.schema.build import build_from_schema
from whathappened.sheets.schema import dod


def test_new_character():
    schema_data = dod.CharacterSheet.model_json_schema()
    data = build_from_schema(schema_data)
    assert data
    assert data["system"] == "dod"
    assert data["meta"]
    assert data["meta"]["title"] == "Unknown"
    assert data["meta"]["gamename"] == "Drakar och demoner"
    assert data["character_sheet"]
