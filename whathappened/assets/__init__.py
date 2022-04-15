




import logging
from webassets.script import CommandLineEnvironment

bp = Blueprint('assets', __name__ )

logger = logging.getLogger(__name__)


@bp.cli.command('build')
@with_appcontext
def build():
    """Build bundles."""
    cmdenv = CommandLineEnvironment(current_app.jinja_env.assets_environment, logger)
    cmdenv.build()

@bp.cli.command('watch')
@with_appcontext
def watch():
    """Watch bundles for file changes."""
    cmdenv = CommandLineEnvironment(current_app.jinja_env.assets_environment, logger)
    cmdenv.watch()


@bp.cli.command('clean')
@with_appcontext
def clean():
    """Clean bundles."""
    cmdenv = CommandLineEnvironment(current_app.jinja_env.assets_environment, logger)
    cmdenv.clean()
