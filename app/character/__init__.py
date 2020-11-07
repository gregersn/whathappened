from flask import Blueprint

from app import assets  # noqa: F401 isort:skip

bp = Blueprint('character', __name__, template_folder="templates")
api = Blueprint('characterapi', __name__, template_folder="templates")

from . import routes  # noqa: E402, F401 isort:skip


@bp.app_template_filter('datetimeformat')
def datetimeformat(value, format="%Y-%m-%d %H:%M:%S"):
    return value.strftime(format)
