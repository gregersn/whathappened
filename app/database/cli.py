from flask import current_app
from flask.cli import AppGroup, with_appcontext

from alembic.config import Config
from alembic import command

db_cli = AppGroup('db')


@with_appcontext
@db_cli.command('history')
def history():
    """Show revision history."""
    alembic_cfg = Config("./migrations/alembic.ini")
    command.history(alembic_cfg)


@with_appcontext
@db_cli.command('upgrade')
def upgrade():
    """Upgrade to latest revision."""
    alembic_cfg = Config("./migrations/alembic.ini")
    command.upgrade(alembic_cfg, 'head')


current_app.cli.add_command(db_cli)
