"""Module for the interaction with character sheets in What Happened?"""

from webassets.env import Environment

from whathappened.core.sheets.schema.utils import fifth, half
from whathappened.web.character.utils import datetimeformat, valuetostring

from . import routes  # noqa: E402, F401 isort:skip
from .blueprints import bp


bp.add_app_template_filter(datetimeformat)
bp.add_app_template_filter(valuetostring)
bp.add_app_template_filter(half)
bp.add_app_template_filter(fifth)


def register_assets(assets: Environment):
    """Register style assets."""
    assets.register(
        "scss_character",
        "scss/character/character.scss",
        filters="pyscss",
        output="css/character.css",
    )
    assets.register(
        "scss_character_general",
        "scss/character/character_general.scss",
        filters="pyscss",
        output="css/character_general.css",
    )
    assets.register(
        "scss_character_coc7e",
        "scss/character/character_coc7e.scss",
        filters="pyscss",
        output="css/character_coc7e.css",
    )

    assets.register(
        "scss_character_tftl",
        "scss/character/character_tftl.scss",
        filters="pyscss",
        output="css/character_tftl.css",
    )
