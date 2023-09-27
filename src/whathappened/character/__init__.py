from flask import Blueprint
from webassets.env import Environment

bp = Blueprint(
    "character", __name__, template_folder="templates", static_folder="static"
)
api = Blueprint("characterapi", __name__, template_folder="templates")

from . import routes  # noqa: E402, F401 isort:skip


@bp.app_template_filter("datetimeformat")
def datetimeformat(value, format: str = "%Y-%m-%d %H:%M:%S"):
    return value.strftime(format)


def register_assets(assets: Environment):
    assets.register(
        "scss_character",
        "scss/character/character.scss",
        filters="pyscss",
        output="css/character.css",
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
