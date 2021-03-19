import logging

from ..core import register_game
from .mechanics import SWD6Mechanics

logger = logging.getLogger(__name__)

register_game('swd6', 'Star Wars', SWD6Mechanics)
