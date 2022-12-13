from pathlib import Path
import logging

from ...sheets.mechanics.core import register_game

from ...sheets.mechanics.tftl.mechanics import TftlMechanics
from .forms import CreateForm  # noqa F401
from whathappened.sheets.schema.build import load_schema, build_from_schema

logger = logging.getLogger(__name__)

CHARACTER_SCHEMA = Path(__file__).parent / '../../sheets/schema/tftl.json'
assert CHARACTER_SCHEMA.is_file()

CHARACTER_TEMPLATE = 'character/tftl/blank_character.json.jinja'
CREATE_TEMPLATE = 'character/tftl/create.html.jinja'

CHARACTER_SHEET_TEMPLATE = 'character/tftl/sheet.html.jinja'


def new_character(title: str, **kwargs):
    schema = load_schema(CHARACTER_SCHEMA)

    nc = build_from_schema(schema)
    nc['title'] = title

    return nc


register_game('tftl', 'Tales from the Loop', TftlMechanics)
