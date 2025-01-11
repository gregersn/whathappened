from whathappened.core.sheets.schema.build import (
    build_from_schema,
    get_schema,
    validate,
)


def test_new_character():
    data = get_schema("landf")
    nc = build_from_schema(data)
    assert nc
    assert nc["system"] == "landf"
    assert nc["meta"]
    assert nc["meta"]["title"] == "Unknown"
    assert nc["meta"]["gamename"] == "Lasers and feelings"
    assert nc["character_sheet"]

    assert not validate(nc, "landf")
