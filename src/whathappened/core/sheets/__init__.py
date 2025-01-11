"""Game sheets handling."""

from whathappened.core.sheets.mechanics import core
from whathappened.core.sheets.mechanics.core import register_game
from whathappened.core.sheets.mechanics.coc7e.mechanics import CoCMechanics
from whathappened.core.sheets.mechanics.dod.mechanics import DoDMechanics
from whathappened.core.sheets.mechanics.landf import LandfMechanics
from whathappened.core.sheets.mechanics.tftl.mechanics import TftlMechanics
from whathappened.core.sheets.mechanics.vaesen import VaesenMechanics, VaesenHQMechanics

from whathappened.core.sheets.schema.base import Gametag

from .mechanics import coc7e  # noqa
from .mechanics import tftl  # noqa


def find_system(tag: Gametag):
    """Find the correct game module."""
    character_module = globals()[tag] if tag in globals() else core

    return character_module


register_game("landf", "Lasers and feelings", LandfMechanics)
register_game("vaesen", "Vaesen", VaesenMechanics)
register_game("vaesenhq", "Vaesen Headquarters", VaesenHQMechanics)
register_game("tftl", "Tales from the Loop", TftlMechanics)
register_game("coc7e", "Call of Cthulhu TM", CoCMechanics)
register_game("dod", "Drakar och demoner", DoDMechanics)
