from pathlib import Path

from whathappened.config import Config

from ...core.userassets.models import Asset, AssetFolder


def resolve_system_path(o: AssetFolder | Asset):
    return Path(Config.UPLOAD_FOLDER) / o.get_path()
