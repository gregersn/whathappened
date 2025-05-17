"""Userassets utils."""

from pathlib import Path
from typing import Union

from flask import current_app


from ...core.userassets.models import Asset, AssetFolder


def resolve_system_path(o: Union[AssetFolder, Asset]):
    """Resolve the system path of an assetfolder or asset."""
    return Path(current_app.config["UPLOAD_FOLDER"]) / o.get_path()
