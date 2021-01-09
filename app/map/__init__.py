from flask import Blueprint

bp = Blueprint('map', __name__, template_folder='templates', static_folder='static')
apibp = Blueprint('mapapi', __name__, template_folder='templates')

from . import routes  # noqa: F401,E402 isort:skip
# from . import views  # noqa: F401, E402 isort:skip
# from . import api  # noqa: F401, E402 isort:skip


def register_assets(assets):
    assets.register('scss_map', 'map/scss/map.scss',
                    filters='pyscss',
                    output='css/map.css')
