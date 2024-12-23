"""Tales from the Loops sheet mechanics."""

import logging
from whathappened.sheets.mechanics.core import new_character
from whathappened.sheets.mechanics.tftl.mechanics import TftlMechanics


__all__ = ["TftlMechanics", "new_character"]

logger = logging.getLogger(__name__)
