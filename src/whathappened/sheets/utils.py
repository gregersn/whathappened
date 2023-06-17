from .schema import build_from_schema, load_schema, SCHEMA_DIR


def create_sheet(system: str):
    """Create a default sheet based on schma for SYSTEM."""
    schema = load_schema(SCHEMA_DIR / system)
    sheet = build_from_schema(schema)

    return sheet
