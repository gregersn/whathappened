import logging
from ...sheets.mechanics.coc7e.mechanics import CoCMechanics
from ...sheets.mechanics.coc7e.mechanics import CHARACTER_SCHEMA  # noqa F401


logger = logging.getLogger(__name__)

# This is not pretty
from .forms import CreateForm  # noqa F401
from .routes import view  # noqa F401

CREATE_TEMPLATE = "character/coc7e/create.html.jinja"

from whathappened.sheets.mechanics.coc7e import new_character
