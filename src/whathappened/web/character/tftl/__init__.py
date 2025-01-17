"""Tftl web specific things."""

from whathappened.core.sheets.mechanics.core import new_character

CREATE_TEMPLATE = "character/tftl/create.html.jinja"
CHARACTER_SHEET_TEMPLATE = "character/tftl/sheet.html.jinja"

__all__ = ["new_character"]
