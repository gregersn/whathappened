from pathlib import Path
from flask import current_app

from ...core.userassets.models import Asset, AssetFolder


def resolve_system_path(o: AssetFolder | Asset):
    return Path(current_app.config["UPLOAD_FOLDER"]) / o.get_path()
