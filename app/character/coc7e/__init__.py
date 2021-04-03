import logging
import json
import jinja2
import time
from typing import Literal
from app.character.schema import load_schema, build_from_schema


from .mechanics import CoCMechanics
from .mechanics import schema_file  # noqa F401

from ..core import register_game

logger = logging.getLogger(__name__)


# This is not pretty
GameType = Literal["Classic (1920's)", "Modern"]
GameTypes = ["Classic (1920's)", "Modern"]
from .forms import CreateForm  # noqa F401
from .routes import view  # noqa F401

CHARACTER_TEMPLATE = 'character/coc7e/blank_character.json.jinja'
CREATE_TEMPLATE = 'character/coc7e/create.html.jinja'


def new_character(title: str, gametype: GameType, **kwargs):
    schema = load_schema(schema_file)

    nc = build_from_schema(schema)
    nc['title'] = title

    return nc


register_game('coc7e', 'Call of Cthulhu TM', CoCMechanics)
