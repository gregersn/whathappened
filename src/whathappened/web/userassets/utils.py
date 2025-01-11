from pathlib import Path
from flask import current_app

from typing import Union

from ...core.userassets.models import Asset, AssetFolder


def resolve_system_path(o: Union[AssetFolder, Asset]):
    return Path(current_app.config["UPLOAD_FOLDER"]) / o.get_path()
