"""Game sheets handling."""

from whathappened.sheets.mechanics import core
from whathappened.sheets.mechanics.core import register_game
from whathappened.sheets.mechanics.coc7e.mechanics import CoCMechanics
from whathappened.sheets.mechanics.dod.mechanics import DoDMechanics
from whathappened.sheets.mechanics.tftl.mechanics import TftlMechanics

from whathappened.sheets.schema.base import Gametag

from .mechanics import coc7e  # noqa
from .mechanics import tftl  # noqa


def find_system(tag: Gametag):
    """Find the correct game module."""
    character_module = globals()[tag] if tag in globals() else core

    return character_module


register_game("landf", "Lasers and Feelings")
register_game("vaesen", "Vaesen")
register_game("tftl", "Tales from the Loop", TftlMechanics)
register_game("coc7e", "Call of Cthulhu TM", CoCMechanics)
register_game("dod", "Drakar och demoner", DoDMechanics)
