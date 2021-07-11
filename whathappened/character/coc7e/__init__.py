from os import path
import pathlib
import logging
import json
import jinja2
import time
from flask import current_app
from typing import Literal


from .mechanics import CoCMechanics
from .mechanics import CHARACTER_SCHEMA  # noqa F401

from ..core import register_game

logger = logging.getLogger(__name__)


from .forms import CreateForm  # noqa F401
from .routes import view  # noqa F401

CHARACTER_TEMPLATE = 'character/coc7e/blank_character.json.jinja'
CREATE_TEMPLATE = 'character/coc7e/create.html.jinja'


def new_character(title: str, gametype: GameType, **kwargs):
    templateloader = jinja2 \
        .FileSystemLoader(searchpath=current_app.root_path + "/character/templates/")
    templateenv = jinja2.Environment(loader=templateloader)
    template = templateenv.get_template(CHARACTER_TEMPLATE)
    gtype = gametype
    return json.loads(template.render(title=title,
                                      timestamp=time.time(),
                                      gametype=gtype))


register_game('coc7e', 'Call of Cthulhu TM', CoCMechanics)
