import yaml
import logging
import pathlib

from ..core import register_game
from .mechanics import SWD6Mechanics

logger = logging.getLogger(__name__)

BLANK_CHARACTER = pathlib.Path(
    __file__).parent.joinpath('blank_character.yaml')

CHARACTER_SHEET_TEMPLATE = 'character/swd6/sheet.html.jinja'


def new_character(title: str, **kwargs):
    with open(BLANK_CHARACTER, 'r') as f:
        data = yaml.safe_load(f)
        data['meta']['title'] = title

        return data


register_game('swd6', 'Star Wars WEG', SWD6Mechanics)
