import os
import logging
import pathlib

from app.character.schema import load_schema, build_from_schema

from ..core import register_game
from .mechanics import SWD6Mechanics

logger = logging.getLogger(__name__)

schema_file = os.path.join(os.path.dirname(__file__), '../schema/swd6.yaml')

BLANK_CHARACTER = pathlib.Path(
    __file__).parent.joinpath('blank_character.yaml')

CHARACTER_SHEET_TEMPLATE = 'character/swd6/sheet.html.jinja'


def new_character(title: str, **kwargs):
    schema = load_schema(schema_file)

    nc = build_from_schema(schema)
    nc['title'] = title

    return nc


register_game('swd6', 'Star Wars WEG', SWD6Mechanics)
