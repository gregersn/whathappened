"""Special cases for Call of Cthulhu."""

import logging
from whathappened.sheets.mechanics.coc7e import new_character_v1
from .forms import CreateForm
from .routes import view

logger = logging.getLogger(__name__)

CREATE_TEMPLATE = "character/coc7e/create.html.jinja"

__all__ = ["CreateForm", "view", "new_character_v1"]
