from flask import Blueprint

bp = Blueprint(
    "main", __name__, template_folder="../templates", static_folder="../static"
)
api = Blueprint("main", __name__)
