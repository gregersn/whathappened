from flask import Blueprint


bp = Blueprint('campaign', __name__)

from . import routes  # noqa: F401,E402 isort:skip
