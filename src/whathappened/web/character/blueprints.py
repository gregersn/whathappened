"""Character blueprints."""

from flask import Blueprint

bp = Blueprint(
    "character", __name__, template_folder="templates", static_folder="static"
)
api = Blueprint("characterapi", __name__, template_folder="templates")
