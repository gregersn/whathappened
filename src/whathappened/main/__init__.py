import logging
import subprocess
from flask import Blueprint

bp = Blueprint("main", __name__)
api = Blueprint("main", __name__)

from . import routes  # noqa: E402, F401 isort:skip

logger = logging.getLogger(__name__)


@bp.cli.command("build")
def build():
    logger.debug("Build stuff")
    project_path = "./frontend"
    subprocess.run("npm run build", cwd=project_path, check=True, shell=True)


@bp.cli.command("watch")
def watch():
    logger.debug("Watch stuff")
    project_path = "./frontend"
    subprocess.run("npm run watch", cwd=project_path, check=True, shell=True)
