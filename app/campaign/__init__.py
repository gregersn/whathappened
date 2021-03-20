from flask import Blueprint
from flask_assets import Environment


bp = Blueprint('campaign', __name__,
               template_folder='templates',
               static_folder='static')
apibp = Blueprint('campaignapi', __name__, template_folder='templates')

from . import routes  # noqa: F401,E402 isort:skip
from . import views  # noqa: F401, E402 isort:skip
from . import api  # noqa: F401, E402 isort:skip
from .models import Campaign  # noqa: F401, E402 isort:skip


def register_assets(assets: Environment):
    assets.register('scss_campaign',
                    'campaign/scss/campaign.scss',
                    filters='pyscss',
                    output='css/campaign.css')

    assets.register('scss_handout',
                    'campaign/scss/handout.scss',
                    filters='pyscss',
                    output='css/handout.css')
