import logging

logger = logging.getLogger(__name__)

from .forms import CreateForm  # noqa F401
from .routes import view  # noqa F401

CREATE_TEMPLATE = "character/coc7e/create.html.jinja"

from whathappened.sheets.mechanics.coc7e import new_character
