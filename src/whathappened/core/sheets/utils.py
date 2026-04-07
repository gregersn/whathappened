"""Miscellanous character sheet utilities."""

from .schema.base import Gametag
from .schema.build import build_from_schema, get_schema


def create_sheet(system: Gametag):
    """Create a default sheet based on schma for SYSTEM."""
    schema = get_schema(system)
    sheet = build_from_schema(schema)

    return sheet
