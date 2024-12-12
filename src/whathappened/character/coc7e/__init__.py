import logging
from whathappened.sheets.mechanics.coc7e import new_character

from .forms import CreateForm  # noqa F401
from .routes import view  # noqa F401

logger = logging.getLogger(__name__)
CREATE_TEMPLATE = "character/coc7e/create.html.jinja"


__all__ = ["new_character"]
