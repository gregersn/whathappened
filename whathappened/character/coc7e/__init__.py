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


register_game('coc7e', 'Call of Cthulhu TM', CoCMechanics)
