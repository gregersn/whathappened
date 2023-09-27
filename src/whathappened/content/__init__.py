from flask import Blueprint

bp = Blueprint("content", __name__, template_folder="templates", static_folder="static")
apibp = Blueprint("contentapi", __name__)

from .models import Folder  # noqa: F401,E402 isort:skip
from . import routes  # noqa: F401,E402 isort:skip
