from whathappened.sheets.schema.build import build_from_schema
from whathappened.sheets.schema import landf


def test_new_character():
    schema_data = landf.CharacterSheet.model_json_schema()
    data = build_from_schema(schema_data)
    assert data
    assert data["system"] == "landf"
    assert data["meta"]
    assert data["meta"]["title"] == "Unknown"
    assert data["meta"]["gamename"] == "Lasers and feelings"
    assert data["character_sheet"]
