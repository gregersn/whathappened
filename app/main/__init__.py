from flask import Blueprint

bp = Blueprint('main', __name__, template_folder='templates')
api = Blueprint('main', __name__, template_folder='templates')

from . import routes  # noqa: E402, F401 isort:skip
