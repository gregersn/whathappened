from flask import Blueprint

from app import assets  # noqa: F401 isort:skip

bp = Blueprint('character', __name__)
api = Blueprint('characterapi', __name__)

from . import routes  # noqa: E402, F401 isort:skip
