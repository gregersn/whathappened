from flask import Blueprint
from flask_assets import Environment


bp = Blueprint('character', __name__, template_folder="templates",
               static_folder="static")
api = Blueprint('characterapi', __name__, template_folder="templates")

from . import routes  # noqa: E402, F401 isort:skip


@bp.app_template_filter('datetimeformat')
def datetimeformat(value, format: str = "%Y-%m-%d %H:%M:%S"):
    return value.strftime(format)


def register_assets(assets: Environment):
    assets.register('scss_character', 'character/scss/character.scss',
                    filters='pyscss',
                    output='css/character.css')

    # TODO: Move this into register_game(?)
    assets.register('scss_character_coc7e',
                    'character/scss/character_coc7e.scss',
                    filters='pyscss',
                    output='css/character_coc7e.css')

    assets.register('scss_character_tftl',
                    'character/scss/character_tftl.scss',
                    filters='pyscss',
                    output='css/character_tftl.css')
