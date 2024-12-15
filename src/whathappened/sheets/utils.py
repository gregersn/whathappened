"""Miscellanous character sheet utilities."""

from .schema.build import get_schema
from .schema import build_from_schema
from .schema.base import Gametag


def create_sheet(system: Gametag):
    """Create a default sheet based on schma for SYSTEM."""
    schema = get_schema(system)
    sheet = build_from_schema(schema)

    return sheet
