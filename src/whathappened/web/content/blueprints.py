"""Content blueprints."""

from flask import Blueprint

bp = Blueprint("content", __name__, template_folder="templates", static_folder="static")
apibp = Blueprint("contentapi", __name__)
