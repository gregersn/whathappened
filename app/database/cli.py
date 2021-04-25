import click
from flask import current_app
from flask.cli import with_appcontext

from alembic.config import Config
from alembic import command


@click.group()
def db():
    pass


@db.command()
@click.option('-d', '--directory', default=None,
              help=('Migration script directory (default is "migrations")'))
@click.option('-v', '--verbose', is_flag=True, help='Use more verbose output')
@with_appcontext
def current(directory, verbose):
    """Display the current revision for each database."""
    alembic_cfg = Config(directory or "./migrations/alembic.ini")
    command.current(alembic_cfg, verbose=verbose)


@db.command('history')
@with_appcontext
def history():
    """Show revision history."""
    alembic_cfg = Config("./migrations/alembic.ini")
    command.history(alembic_cfg)


@db.command('upgrade')
@click.option('-d', '--directory', default=None,
              help=('Migration script directory (default is "migrations")'))
@click.option('--sql', is_flag=True,
              help=('Don\'t emit SQL to database - dump to standard output '
                    'instead'))
@click.option('--tag', default=None,
              help=('Arbitrary "tag" name - can be used by custom env.py '
                    'scripts'))
@click.option('-x', '--x-arg', multiple=True,
              help='Additional arguments consumed by custom env.py scripts')
@click.argument('revision', default='head')
@with_appcontext
def upgrade(directory, sql, tag, x_arg, revision):
    """Upgrade to latest revision."""
    alembic_cfg = Config(directory or "./migrations/alembic.ini")
    command.upgrade(alembic_cfg, revision, sql, tag)


@db.command('downgrade')
@click.option('-d', '--directory', default=None,
              help=('Migration script directory (default is "migrations")'))
@click.option('--sql', is_flag=True,
              help=('Don\'t emit SQL to database - dump to standard output '
                    'instead'))
@click.option('--tag', default=None,
              help=('Arbitrary "tag" name - can be used by custom env.py '
                    'scripts'))
@click.option('-x', '--x-arg', multiple=True,
              help='Additional arguments consumed by custom env.py scripts')
@click.argument('revision', default='-1')
@with_appcontext
def downgrade(directory, sql=False, tag=None, x_arg=None, revision='-1'):
    """downgrade to previous revision."""
    alembic_cfg = Config(directory or "./migrations/alembic.ini")
    if sql and revision == '-1':
        revision = 'head:-1'
    command.downgrade(alembic_cfg, revision, sql, tag)


@db.command('revision')
@click.option('-d', '--directory', default=None,
              help=('Migration script directory (default is "migrations")'))
@click.option('-m', '--message', help=("Migration messasge"), required=True)
@with_appcontext
def revision(directory, message):
    """Create new revision."""
    alembic_cfg = Config(directory or "./migrations/alembic.ini")
    command.revision(alembic_cfg, autogenerate=True, message=message)


current_app.cli.add_command(db)
