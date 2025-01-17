from whathappened.core.sheets.schema.build import (
    build_from_schema,
    get_schema,
    validate,
)


def test_new_character_from_schema():
    data = get_schema("dod")
    nc = build_from_schema(data)

    assert nc["character_sheet"]["personalia"]["slakte"] == "Människa"
    assert not isinstance(nc["character_sheet"]["fardigheter"], str)

    assert not validate(nc, "dod")

    assert nc["character_sheet"]["personalia"]["alder"] == "Ung"
