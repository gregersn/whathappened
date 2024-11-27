"""Miscellanous character sheet utilities."""

from .schema.build import get_schema
from .schema import build_from_schema


def create_sheet(system: str):
    """Create a default sheet based on schma for SYSTEM."""
    schema = get_schema(system)
    sheet = build_from_schema(schema)

    return sheet
