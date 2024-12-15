"""Tales from the Loops sheet mechanics."""

from pathlib import Path
import logging
from typing import Optional

from whathappened.sheets.mechanics.tftl.mechanics import TftlMechanics

from whathappened.sheets.schema.build import get_schema, build_from_schema

__all__ = ["TftlMechanics"]

logger = logging.getLogger(__name__)

# CHARACTER_SCHEMA = Path(__file__).parent / "../../../sheets/schema/tftl.json"
# assert CHARACTER_SCHEMA.is_file()

# CHARACTER_TEMPLATE = "character/tftl/blank_character.json.jinja"


def new_character(title: str, version: Optional[str] = None, **kwargs):
    """Create a new character."""
    schema = get_schema("tftl")

    nc = build_from_schema(schema)
    nc["title"] = title
    nc["version"] = version

    return nc
