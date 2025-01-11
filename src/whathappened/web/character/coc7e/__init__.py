from .forms import CreateForm
from .routes import view

# from ...character.coc7e import new_character

CREATE_TEMPLATE = "character/coc7e/create.html.jinja"

__all__ = ["CreateForm", "view"]
