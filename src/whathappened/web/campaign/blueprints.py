from flask import Blueprint

bp = Blueprint(
    "campaign", __name__, template_folder="templates", static_folder="static"
)
apibp = Blueprint("campaignapi", __name__)
