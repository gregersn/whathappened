"""Call of Cthulhu schema."""

from whathappened.core.sheets.schema.coc7e.sheet import CallofCthulhu7e

from .migrations import migrations

CharacterSheet = CallofCthulhu7e

__all__ = ["migrations", "CharacterSheet"]
