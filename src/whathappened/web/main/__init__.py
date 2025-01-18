"""Main cli commands for web."""

import logging
import subprocess

from .blueprints import bp
from . import routes  # noqa: E402, F401 isort:skip

logger = logging.getLogger(__name__)


@bp.cli.command("build")
def build():
    """Build frontend stuff."""
    logger.debug("Build stuff")
    project_path = "./frontend"
    subprocess.run("npm run build", cwd=project_path, check=True, shell=True)


@bp.cli.command("watch")
def watch():
    """Watch build frontend stuff."""
    logger.debug("Watch stuff")
    project_path = "./frontend"
    subprocess.run("npm run watch", cwd=project_path, check=True, shell=True)
