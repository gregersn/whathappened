from pathlib import Path

from .schema import build_from_schema, load_schema, SCHEMA_DIR


def new_sheet(schema_path: Path):
    assert schema_path.is_file()
    schema = load_schema(schema_path)
    sheet = build_from_schema(schema)
    sheet['schema'] = str(schema_path)

    return sheet


def create_sheet(system: str):
    """Create a default sheet based on schma for SYSTEM."""
    schema = load_schema(SCHEMA_DIR / system)
    sheet = build_from_schema(schema)

    return sheet
