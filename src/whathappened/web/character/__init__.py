import math
from webassets.env import Environment

from . import routes  # noqa: E402, F401 isort:skip
from .blueprints import bp


@bp.app_template_filter("datetimeformat")
def datetimeformat(value, formatstring: str = "%Y-%m-%d %H:%M:%S"):
    """Jinja filter for formatting datetimes."""
    return value.strftime(formatstring)


@bp.app_template_filter("valuetostring")
def valuetostring(value):
    if isinstance(value, dict):
        return ", ".join(f"{k}: {v}" for k, v in value.items())
    return value


@bp.app_template_filter("half")
def half(value):
    if not value:
        return 0
    if isinstance(value, str):
        try:
            value = int(value, 10)
        except ValueError:
            return 0
    return math.floor(value / 2)


@bp.app_template_filter("fifth")
def fifth(value):
    if not value:
        return 0
    if isinstance(value, str):
        try:
            value = int(value, 10)
        except ValueError:
            return 0
    return math.floor(value / 5)


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
