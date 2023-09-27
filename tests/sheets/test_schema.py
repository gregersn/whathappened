from whathappened.sheets.schema.build import SCHEMA_DIR, build_from_schema, get_schema, load_schema, validate


def test_load_schema():
    schema = load_schema(SCHEMA_DIR / "landf.yaml")

    assert schema

    assert schema['type'] == "object"
    assert schema['properties']['meta']['properties']['gamename']['const'] == "Lasers and feelings", schema


def test_build_from_schema():
    schema = get_schema("landf")

    data = build_from_schema(schema)

    assert data

    assert data['meta']['gamename'] == "Lasers and feelings"
    assert data['character_sheet']['name'] == "Ace"


def test_validate():
    schema = get_schema("landf")
    data = build_from_schema(schema)

    assert not validate(data, "landf")

    del data['character_sheet']['name']
    errors = validate(data, "landf")

    assert errors
