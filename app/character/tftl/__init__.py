import os
import json
import time
import jinja2
import logging

from ..core import register_game

from .mechanics import TftlMechanics
from .forms import CreateForm  # noqa F401
from .routes import view  # noqa F401
import yaml

logger = logging.getLogger(__name__)

schema_file = os.path.join(os.path.dirname(__file__), '../schema/tftl.json')

CHARACTER_TEMPLATE = 'character/tftl/blank_character.json.jinja'
BLANK_CHARACTER = 'app/character/tftl/blank_tftl.yaml'


def new_character(title):
    with open('app/character/tftl/blank_tftl.yaml', 'r') as f:
        character_data = yaml.safe_load(f)

        return character_data


register_game('tftl', 'Tales from the Loop', TftlMechanics)
