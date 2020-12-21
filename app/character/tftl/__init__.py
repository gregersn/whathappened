import os
import json
import time
import jinja2
import logging

from ..core import register_game

from .mechanics import TftlMechanics
from .forms import CreateForm  # noqa F401
from .routes import view  # noqa F401

logger = logging.getLogger(__name__)

schema_file = os.path.join(os.path.dirname(__file__), '../schema/tftl.json')

CHARACTER_TEMPLATE = 'character/tftl/blank_character.json.jinja'


def new_character(title):
    templateloader = jinja2 \
                     .FileSystemLoader(searchpath="./app/character/templates/")
    templateenv = jinja2.Environment(loader=templateloader)
    template = templateenv.get_template(CHARACTER_TEMPLATE)
    return json.loads(template.render(title=title,
                                      timestamp=time.time(),
                                      ))


register_game('tftl', 'Tales from the Loop', TftlMechanics)
