from .schema import build_from_schema, load_schema, SCHEMA_DIR


def create_sheet(system: str):
    schema = load_schema(SCHEMA_DIR / system)
    sheet = build_from_schema(schema)

    return sheet
