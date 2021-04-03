import os
import logging

from ..core import register_game

from .mechanics import TftlMechanics
from .forms import CreateForm  # noqa F401
from app.character.schema import load_schema, build_from_schema

logger = logging.getLogger(__name__)

schema_file = os.path.join(os.path.dirname(__file__), '../schema/tftl.json')

CHARACTER_TEMPLATE = 'character/tftl/blank_character.json.jinja'
CREATE_TEMPLATE = 'character/tftl/create.html.jinja'

CHARACTER_SHEET_TEMPLATE = 'character/tftl/sheet.html.jinja'


def new_character(title: str, **kwargs):
    schema = load_schema(schema_file)

    nc = build_from_schema(schema)
    nc['title'] = title

    return nc


register_game('tftl', 'Tales from the Loop', TftlMechanics)
