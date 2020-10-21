from flask import Blueprint

bp = Blueprint('main', __name__, template_folder='templates')
api = Blueprint('main', __name__, template_folder='templates')

from . import routes  # noqa: E402, F401 isort:skip

import logging
import click

from pywebpack import WebpackProject

logger = logging.getLogger(__name__)


@bp.cli.command('build')
def build():
    logger.debug("Build stuff")
    project_path = './frontend'
    project = WebpackProject(project_path)

    project.build()

@bp.cli.command('watch')
def watch():
    logger.debug("Watch stuff")
    project_path = './frontend'
    project = WebpackProject(project_path)

    project.run('watch')

