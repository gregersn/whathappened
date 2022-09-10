from pywebpack import WebpackProject
import logging

# bp = Blueprint('main', __name__ )
# api = Blueprint('main', __name__ )

from . import routes  # noqa: E402, F401 isort:skip

logger = logging.getLogger(__name__)


# @bp.cli.command('build')
def build():
    logger.debug("Build stuff")
    project_path = './frontend'
    project = WebpackProject(project_path)

    project.build()


# @bp.cli.command('watch')
def watch():
    logger.debug("Watch stuff")
    project_path = './frontend'
    project = WebpackProject(project_path)

    project.run('watch')
