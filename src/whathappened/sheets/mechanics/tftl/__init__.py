"""Tales from the Loops sheet mechanics."""

from pathlib import Path
import logging

from whathappened.sheets.mechanics.tftl.mechanics import TftlMechanics

from whathappened.sheets.schema.build import get_schema, build_from_schema

__all__ = ["TftlMechanics"]

logger = logging.getLogger(__name__)


def new_character(title: str, **kwargs):
    """Create a new character."""
    schema = get_schema("tftl")

    nc = build_from_schema(schema)
    nc["title"] = title

    return nc
