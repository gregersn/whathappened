from re import template
from flask import Blueprint


bp = Blueprint('campaign', __name__, template_folder='templates')

from . import routes  # noqa: F401,E402 isort:skip
